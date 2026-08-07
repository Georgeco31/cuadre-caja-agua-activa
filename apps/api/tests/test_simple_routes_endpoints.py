import importlib.util
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.delivery_route import DeliveryRoute
from app.models.expense import Expense
from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.route_load import RouteLoad
from app.models.sale import Sale
from app.models.simple_route import (
    SimpleRouteCashReceipt,
    SimpleRouteCollection,
    SimpleRouteExpense,
    SimpleRouteSale,
    SimpleRouteSheet,
    SimpleRouteTrip,
    SimpleRouteTripItem,
)
from app.models.user import User
from app.models.vehicle import Vehicle


def test_admin_and_operator_can_create_independent_simple_route(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, session_factory = api_client
    admin = _create_sheet(client, api_auth_headers, seller="George")
    operator = _create_sheet(
        client,
        api_operator_auth_headers,
        seller="Vendedor operativo",
    )

    assert admin.status_code == 201
    assert operator.status_code == 201
    assert admin.json()["status"] == "draft"
    assert admin.json()["employee_id"] is None
    assert admin.json()["vehicle_id"] is None
    with session_factory() as session:
        assert session.query(SimpleRouteSheet).count() == 2
        assert session.query(Sale).count() == 0
        assert session.query(InventoryMovement).count() == 0


def test_multiple_trips_accumulate_out_and_return_and_block_excess(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]
    trip_one = _add_trip(client, api_auth_headers, sheet_id).json()
    trip_two = _add_trip(client, api_auth_headers, sheet_id).json()

    assert trip_one["trip_number"] == 1
    assert trip_two["trip_number"] == 2
    assert _add_trip_item(
        client, api_auth_headers, sheet_id, trip_one["id"], "out", "Bidón lleno", "120"
    ).status_code == 201
    assert _add_trip_item(
        client, api_auth_headers, sheet_id, trip_one["id"], "return", "Bidón lleno", "20"
    ).status_code == 201
    assert _add_trip_item(
        client, api_auth_headers, sheet_id, trip_two["id"], "out", "Bidón lleno", "50"
    ).status_code == 201
    assert _add_trip_item(
        client, api_auth_headers, sheet_id, trip_two["id"], "return", "Bidón lleno", "10"
    ).status_code == 201
    blocked = _add_trip_item(
        client, api_auth_headers, sheet_id, trip_two["id"], "return", "Bidón lleno", "141"
    )
    settlement = client.get(
        f"/api/v1/simple-routes/{sheet_id}/settlement",
        headers=api_auth_headers,
    ).json()

    assert blocked.status_code == 400
    product = settlement["products"][0]
    assert Decimal(product["total_out"]) == Decimal("170.000")
    assert Decimal(product["total_returned"]) == Decimal("30.000")
    assert Decimal(product["physical_sold"]) == Decimal("140.000")


@pytest.mark.parametrize(
    ("sale_type", "paid", "expected_paid", "expected_pending"),
    [
        ("cash", None, "20.00", "0.00"),
        ("credit", None, "0.00", "20.00"),
        ("partial", "7.50", "7.50", "12.50"),
    ],
)
def test_route_sale_types_are_calculated_independently(
    api_client,
    api_auth_headers,
    sale_type: str,
    paid: str | None,
    expected_paid: str,
    expected_pending: str,
) -> None:
    client, session_factory = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]
    before = _official_counts(session_factory)

    response = _add_sale(client, api_auth_headers, sheet_id, sale_type, paid)

    assert response.status_code == 201, response.json()
    sale = response.json()
    assert Decimal(sale["total_amount"]) == Decimal("20.00")
    assert Decimal(sale["paid_amount"]) == Decimal(expected_paid)
    assert Decimal(sale["pending_amount"]) == Decimal(expected_pending)
    assert Decimal(sale["remaining_amount"]) == Decimal(expected_pending)
    with session_factory() as session:
        assert session.query(SimpleRouteSale).count() == 1
    assert _official_counts(session_factory) == before


def test_sale_type_validation_is_clear(api_client, api_auth_headers) -> None:
    client, _ = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]

    wrong_cash = _add_sale(client, api_auth_headers, sheet_id, "cash", "10")
    wrong_credit = _add_sale(client, api_auth_headers, sheet_id, "credit", "1")
    wrong_partial = _add_sale(client, api_auth_headers, sheet_id, "partial", "20")

    assert wrong_cash.status_code == 400
    assert wrong_credit.status_code == 400
    assert wrong_partial.status_code == 400


def test_collection_increases_expected_cash_and_reduces_internal_credit_balance(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]
    sale = _add_sale(client, api_auth_headers, sheet_id, "credit").json()
    before = _official_counts(session_factory)

    collection = client.post(
        f"/api/v1/simple-routes/{sheet_id}/collections",
        headers=api_auth_headers,
        json={
            "simple_route_sale_id": sale["id"],
            "customer_name": "Cliente informal",
            "amount": "5.00",
        },
    )
    detail = client.get(
        f"/api/v1/simple-routes/{sheet_id}", headers=api_auth_headers
    ).json()
    settlement = client.get(
        f"/api/v1/simple-routes/{sheet_id}/settlement", headers=api_auth_headers
    ).json()

    assert collection.status_code == 201
    assert Decimal(detail["sales"][0]["remaining_amount"]) == Decimal("15.00")
    assert Decimal(settlement["collections_total"]) == Decimal("5.00")
    assert Decimal(settlement["expected_cash"]) == Decimal("5.00")
    assert _official_counts(session_factory) == before


def test_route_expense_reduces_expected_cash_without_official_expense(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]
    _add_sale(client, api_auth_headers, sheet_id, "cash")
    before = _official_counts(session_factory)

    response = client.post(
        f"/api/v1/simple-routes/{sheet_id}/expenses",
        headers=api_auth_headers,
        json={"description": "Combustible", "category": "fuel", "amount": "3.25"},
    )
    settlement = client.get(
        f"/api/v1/simple-routes/{sheet_id}/settlement", headers=api_auth_headers
    ).json()

    assert response.status_code == 201
    assert Decimal(settlement["expenses_total"]) == Decimal("3.25")
    assert Decimal(settlement["expected_cash"]) == Decimal("16.75")
    assert _official_counts(session_factory) == before


def test_settlement_detects_product_and_cash_differences(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]
    trip = _add_trip(client, api_auth_headers, sheet_id).json()
    _add_trip_item(
        client, api_auth_headers, sheet_id, trip["id"], "out", "Bidón lleno", "10"
    )
    _add_trip_item(
        client, api_auth_headers, sheet_id, trip["id"], "return", "Bidón lleno", "2"
    )
    _add_sale(client, api_auth_headers, sheet_id, "cash", quantity="7", unit_price="2")

    settled = client.post(
        f"/api/v1/simple-routes/{sheet_id}/settle",
        headers=api_auth_headers,
        json={"cash_delivered": "13.00"},
    )
    settlement = client.get(
        f"/api/v1/simple-routes/{sheet_id}/settlement", headers=api_auth_headers
    ).json()

    assert settled.status_code == 200
    assert settlement["status"] == "with_difference"
    assert Decimal(settlement["products"][0]["physical_difference"]) == Decimal("1.000")
    assert Decimal(settlement["cash_difference"]) == Decimal("-1.00")


def test_balanced_route_and_settled_sheet_are_locked(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]
    trip = _add_trip(client, api_auth_headers, sheet_id).json()
    _add_trip_item(
        client, api_auth_headers, sheet_id, trip["id"], "out", "Bidón lleno", "10"
    )
    _add_sale(client, api_auth_headers, sheet_id, "cash", quantity="10", unit_price="2")
    client.post(
        f"/api/v1/simple-routes/{sheet_id}/settle",
        headers=api_auth_headers,
        json={"cash_delivered": "20.00"},
    )

    settlement = client.get(
        f"/api/v1/simple-routes/{sheet_id}/settlement", headers=api_auth_headers
    ).json()
    edit = client.patch(
        f"/api/v1/simple-routes/{sheet_id}",
        headers=api_auth_headers,
        json={"route_label": "Cambio tardío"},
    )

    assert settlement["status"] == "balanced"
    assert edit.status_code == 409


def test_cancel_requires_reason_and_operator_cannot_use_admin_actions(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    sheet_id = _create_sheet(client, api_operator_auth_headers).json()["id"]

    missing = client.post(
        f"/api/v1/simple-routes/{sheet_id}/cancel",
        headers=api_auth_headers,
        json={"reason": "   "},
    )
    operator_settle = client.post(
        f"/api/v1/simple-routes/{sheet_id}/settle",
        headers=api_operator_auth_headers,
        json={"cash_delivered": "0"},
    )
    operator_cancel = client.post(
        f"/api/v1/simple-routes/{sheet_id}/cancel",
        headers=api_operator_auth_headers,
        json={"reason": "No autorizado"},
    )
    cancelled = client.post(
        f"/api/v1/simple-routes/{sheet_id}/cancel",
        headers=api_auth_headers,
        json={"reason": "Ruta no realizada"},
    )

    assert missing.status_code == 422
    assert operator_settle.status_code == 403
    assert operator_cancel.status_code == 403
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


def test_cash_receipt_is_unique_traceability_and_does_not_change_cash_summary(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    sheet_id = _create_sheet(client, api_auth_headers).json()["id"]
    _add_sale(client, api_auth_headers, sheet_id, "cash")
    client.post(
        f"/api/v1/simple-routes/{sheet_id}/settle",
        headers=api_auth_headers,
        json={"cash_delivered": "20"},
    )
    cash_session_id = _create_cash_session(session_factory)
    summary_before = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/summary", headers=api_auth_headers
    ).json()

    first = client.post(
        f"/api/v1/simple-routes/{sheet_id}/cash-receipt",
        headers=api_auth_headers,
        json={"cash_session_id": cash_session_id, "notes": "Recibido"},
    )
    duplicate = client.post(
        f"/api/v1/simple-routes/{sheet_id}/cash-receipt",
        headers=api_auth_headers,
        json={"cash_session_id": cash_session_id},
    )
    receipts = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/simple-route-cash-receipts",
        headers=api_auth_headers,
    )
    summary_after = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/summary", headers=api_auth_headers
    ).json()

    assert first.status_code == 201, first.json()
    assert duplicate.status_code == 409
    assert len(receipts.json()) == 1
    assert Decimal(receipts.json()[0]["amount"]) == Decimal("20.00")
    assert summary_after == summary_before
    with session_factory() as session:
        assert session.query(SimpleRouteCashReceipt).count() == 1


def test_analytics_are_separate_and_operator_is_blocked(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    first_id = _create_sheet(
        client, api_auth_headers, seller="George", route_label="Norte"
    ).json()["id"]
    second_id = _create_sheet(
        client, api_auth_headers, seller="Ana", route_label="Sur", day=2
    ).json()["id"]
    _add_sale(client, api_auth_headers, first_id, "cash", quantity="5", unit_price="2")
    _add_sale(client, api_auth_headers, second_id, "cash", quantity="3", unit_price="2")

    response = client.get(
        "/api/v1/simple-routes/analytics?date_from=2026-08-01&date_to=2026-08-02",
        headers=api_auth_headers,
    )
    operator = client.get(
        "/api/v1/simple-routes/analytics?date_from=2026-08-01&date_to=2026-08-02",
        headers=api_operator_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert Decimal(body["total_route_sales"]) == Decimal("16.00")
    assert body["top_routes"][0]["label"] == "Norte"
    assert body["top_sellers"][0]["label"] == "George"
    assert body["best_sales_day"]["route_date"] == "2026-08-01"
    assert operator.status_code == 403


def test_august_dry_run_lists_candidates_without_modifying_data(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    official_sale_id = _seed_official_route_sale(session_factory)
    before = _official_counts(session_factory)

    response = client.get(
        "/api/v1/simple-routes/cleanup/august-1-route-sales-dry-run",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["report_date"] == "2026-08-01"
    assert body["modified_records"] == 0
    assert [candidate["sale_id"] for candidate in body["candidates"]] == [official_sale_id]
    assert _official_counts(session_factory) == before


def test_simple_route_endpoints_require_authentication(api_client) -> None:
    client, _ = api_client
    assert client.get("/api/v1/simple-routes").status_code == 401
    assert client.post("/api/v1/simple-routes", json={}).status_code == 401


def test_simple_route_migration_declares_all_tables(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0029_simple_route_sheets.py"
    )
    spec = importlib.util.spec_from_file_location("migration_0029_simple_routes", migration_path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[str] = []
    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda name, *args, **kwargs: created_tables.append(name),
    )
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)

    migration.upgrade()

    assert migration.revision == "0029_simple_routes"
    assert migration.down_revision == "0028_payroll_base"
    assert created_tables == [
        "simple_route_sheets",
        "simple_route_trips",
        "simple_route_trip_items",
        "simple_route_sales",
        "simple_route_sale_items",
        "simple_route_collections",
        "simple_route_expenses",
        "simple_route_audit_logs",
        "simple_route_cash_receipts",
    ]


def _create_sheet(
    client,
    headers,
    *,
    seller: str = "George",
    route_label: str = "Centro",
    day: int = 1,
):
    return client.post(
        "/api/v1/simple-routes",
        headers=headers,
        json={
            "route_date": f"2026-08-{day:02d}",
            "seller_name": seller,
            "route_label": route_label,
        },
    )


def _add_trip(client, headers, sheet_id: int):
    return client.post(
        f"/api/v1/simple-routes/{sheet_id}/trips",
        headers=headers,
        json={},
    )


def _add_trip_item(
    client,
    headers,
    sheet_id: int,
    trip_id: int,
    movement_type: str,
    label: str,
    quantity: str,
):
    return client.post(
        f"/api/v1/simple-routes/{sheet_id}/trips/{trip_id}/items",
        headers=headers,
        json={
            "movement_type": movement_type,
            "item_label": label,
            "item_category": "full_jug",
            "quantity": quantity,
        },
    )


def _add_sale(
    client,
    headers,
    sheet_id: int,
    sale_type: str,
    paid: str | None = None,
    *,
    quantity: str = "2",
    unit_price: str = "10",
):
    payload: dict[str, object] = {
        "customer_name": "Cliente informal",
        "sale_type": sale_type,
        "items": [
            {
                "product_name": "Bidón lleno",
                "item_category": "full_jug",
                "quantity": quantity,
                "unit_price": unit_price,
            }
        ],
    }
    if paid is not None:
        payload["paid_amount"] = paid
    return client.post(
        f"/api/v1/simple-routes/{sheet_id}/sales",
        headers=headers,
        json=payload,
    )


def _official_counts(session_factory) -> dict[str, int]:
    with session_factory() as session:
        return {
            "sales": session.query(Sale).count(),
            "credit_payments": session.query(CreditPayment).count(),
            "expenses": session.query(Expense).count(),
            "inventory_movements": session.query(InventoryMovement).count(),
        }


def _create_cash_session(session_factory) -> int:
    with session_factory() as session:
        user = session.query(User).filter(User.username == "admin").one()
        cash_session = CashSession(
            session_date=date(2026, 8, 1),
            status="open",
            created_by=user.id,
        )
        session.add(cash_session)
        session.commit()
        return cash_session.id


def _seed_official_route_sale(session_factory) -> int:
    with session_factory() as session:
        user = session.query(User).filter(User.username == "admin").one()
        route = DeliveryRoute(
            code="DRY-RUN-ROUTE",
            name="Ruta prueba dry-run",
            expected_daily_cash=Decimal("0"),
        )
        vehicle = Vehicle(
            code="DRY-RUN-VEHICLE",
            name="Vehículo prueba dry-run",
            vehicle_type="truck",
            fuel_type="diesel",
        )
        session.add_all([route, vehicle])
        session.flush()
        source = InventoryLocation(
            code="DRY-RUN-SOURCE",
            name="Origen dry-run",
            location_type="warehouse",
        )
        destination = InventoryLocation(
            code="DRY-RUN-DESTINATION",
            name="Destino dry-run",
            location_type="vehicle",
            vehicle_id=vehicle.id,
        )
        session.add_all([source, destination])
        session.flush()
        route_load = RouteLoad(
            load_number="LOAD-DRY-RUN",
            load_date=date(2026, 8, 1),
            route_id=route.id,
            vehicle_id=vehicle.id,
            source_location_id=source.id,
            destination_location_id=destination.id,
            status="active",
            created_by=user.id,
        )
        session.add(route_load)
        session.flush()
        sale = Sale(
            sale_number="SALE-DRY-RUN",
            sale_date=date(2026, 8, 1),
            route_load_id=route_load.id,
            customer_name_snapshot="Cliente prueba",
            sale_type="cash",
            payment_method="cash",
            status="active",
            total_amount=Decimal("10"),
            paid_amount=Decimal("10"),
            balance_amount=Decimal("0"),
            credit_status="none",
            created_by=user.id,
        )
        session.add(sale)
        session.commit()
        return sale.id
