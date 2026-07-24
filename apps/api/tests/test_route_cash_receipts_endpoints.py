import importlib.util
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_count_item import CashCountItem
from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.delivery_route import DeliveryRoute
from app.models.expense import Expense
from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.route_cash_receipt import RouteCashReceipt
from app.models.route_closure import RouteClosure
from app.models.route_load import RouteLoad
from app.models.sale import Sale
from app.models.user import User
from app.models.vehicle import Vehicle


def test_create_receipt_defaults_amount_and_only_adds_traceability(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    context = _seed_context(session_factory, "01", delivered="115.00")

    with session_factory() as session:
        before = _operational_counts(session)
    summary_before = client.get(
        f"/api/v1/cash-sessions/{context['cash_session_id']}/summary",
        headers=api_auth_headers,
    ).json()

    response = _create_receipt(
        client,
        api_auth_headers,
        context,
        received_amount=None,
        notes="  Entrega recibida en caja  ",
    )

    assert response.status_code == 201, response.json()
    receipt = response.json()
    assert receipt["receipt_number"].startswith("RCR-20260718-")
    assert receipt["receipt_date"] == "2026-07-18"
    assert receipt["route_closure_id"] == context["closure_id"]
    assert receipt["cash_session_id"] == context["cash_session_id"]
    assert receipt["route_load_id"] == context["route_load_id"]
    assert receipt["route_id"] == context["route_id"]
    assert receipt["vehicle_id"] == context["vehicle_id"]
    assert receipt["closure_number_snapshot"] == context["closure_number"]
    assert receipt["route_name_snapshot"] == context["route_name"]
    assert receipt["vehicle_name_snapshot"] == context["vehicle_name"]
    assert Decimal(receipt["delivered_cash_total"]) == Decimal("115.00")
    assert Decimal(receipt["received_amount"]) == Decimal("115.00")
    assert Decimal(receipt["difference_amount"]) == Decimal("0.00")
    assert receipt["notes"] == "Entrega recibida en caja"
    assert receipt["status"] == "active"
    assert receipt["route_closure"]["id"] == context["closure_id"]
    assert receipt["cash_session"]["id"] == context["cash_session_id"]

    summary_after = client.get(
        f"/api/v1/cash-sessions/{context['cash_session_id']}/summary",
        headers=api_auth_headers,
    ).json()
    with session_factory() as session:
        assert _operational_counts(session) == before
        closure = session.get(RouteClosure, context["closure_id"])
        assert closure is not None
        assert closure.status == "active"
        assert closure.delivered_cash_total == Decimal("115.00")
    assert summary_after == summary_before


@pytest.mark.parametrize(
    ("received_amount", "expected_difference"),
    [("100.00", "-15.00"), ("130.50", "15.50")],
)
def test_receipt_calculates_negative_and_positive_difference(
    api_client,
    api_auth_headers,
    received_amount: str,
    expected_difference: str,
) -> None:
    client, session_factory = api_client
    context = _seed_context(session_factory, received_amount.replace(".", ""))

    response = _create_receipt(
        client,
        api_auth_headers,
        context,
        received_amount=received_amount,
    )

    assert response.status_code == 201
    assert Decimal(response.json()["difference_amount"]) == Decimal(
        expected_difference,
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"route_closure_id": 1, "cash_session_id": 1},
        {
            "receipt_date": "2026-07-18",
            "route_closure_id": 1,
            "cash_session_id": 1,
            "received_amount": "-0.01",
        },
        {
            "receipt_date": "2026-07-18",
            "route_closure_id": 0,
            "cash_session_id": 1,
        },
    ],
)
def test_receipt_rejects_invalid_payload(
    api_client,
    api_auth_headers,
    payload: dict[str, object],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/route-cash-receipts",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_receipt_validates_closure_and_cash_session_states(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    active = _seed_context(session_factory, "active", day=17)
    voided = _seed_context(
        session_factory,
        "voided",
        day=18,
        closure_status="voided",
    )
    closed = _seed_context(
        session_factory,
        "closed",
        day=19,
        cash_status="closed",
    )

    missing_closure = client.post(
        "/api/v1/route-cash-receipts",
        headers=api_auth_headers,
        json={
            "receipt_date": "2026-07-18",
            "route_closure_id": 999,
            "cash_session_id": active["cash_session_id"],
        },
    )
    missing_cash = client.post(
        "/api/v1/route-cash-receipts",
        headers=api_auth_headers,
        json={
            "receipt_date": "2026-07-18",
            "route_closure_id": active["closure_id"],
            "cash_session_id": 999,
        },
    )
    voided_closure = _create_receipt(client, api_auth_headers, voided)
    closed_cash = _create_receipt(client, api_auth_headers, closed)

    assert missing_closure.status_code == 404
    assert missing_cash.status_code == 404
    assert voided_closure.status_code == 400
    assert "anulado" in voided_closure.json()["detail"]
    assert closed_cash.status_code == 400
    assert "cerrado" in closed_cash.json()["detail"]


def test_duplicate_void_replacement_and_closure_block(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    context = _seed_context(session_factory, "history")
    first = _create_receipt(client, api_auth_headers, context).json()
    duplicate = _create_receipt(client, api_auth_headers, context)
    blocked_closure = client.post(
        f"/api/v1/route-closures/{context['closure_id']}/void",
        headers=api_auth_headers,
        json={"reason": "Cierre incorrecto"},
    )
    missing_reason = client.post(
        f"/api/v1/route-cash-receipts/{first['id']}/void",
        headers=api_auth_headers,
        json={},
    )
    blank_reason = client.post(
        f"/api/v1/route-cash-receipts/{first['id']}/void",
        headers=api_auth_headers,
        json={"reason": "   "},
    )
    voided = client.post(
        f"/api/v1/route-cash-receipts/{first['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Registro duplicado por error"},
    )
    repeated = client.post(
        f"/api/v1/route-cash-receipts/{first['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Otra vez"},
    )
    replacement = _create_receipt(client, api_auth_headers, context)

    assert duplicate.status_code == 409
    assert blocked_closure.status_code == 409
    assert "Primero anule" in blocked_closure.json()["detail"]
    assert missing_reason.status_code == 422
    assert blank_reason.status_code == 422
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    assert voided.json()["void_reason"] == "Registro duplicado por error"
    assert voided.json()["voided_at"] is not None
    assert repeated.status_code == 409
    assert replacement.status_code == 201
    assert replacement.json()["id"] != first["id"]
    with session_factory() as session:
        assert session.query(RouteCashReceipt).count() == 2


def test_list_detail_filters_and_closure_receipt_status(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    first_context = _seed_context(session_factory, "filter-a", day=17)
    second_context = _seed_context(session_factory, "filter-b", day=18)
    before = client.get(
        f"/api/v1/route-closures/{second_context['closure_id']}/cash-receipt",
        headers=api_auth_headers,
    )
    first = _create_receipt(
        client,
        api_auth_headers,
        first_context,
        receipt_date="2026-07-17",
    ).json()
    second = _create_receipt(
        client,
        api_auth_headers,
        second_context,
        receipt_date="2026-07-18",
    ).json()
    client.post(
        f"/api/v1/route-cash-receipts/{first['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Prueba de historial"},
    )

    detail = client.get(
        f"/api/v1/route-cash-receipts/{second['id']}",
        headers=api_auth_headers,
    )
    by_date = client.get(
        "/api/v1/route-cash-receipts"
        "?date_from=2026-07-18&date_to=2026-07-18",
        headers=api_auth_headers,
    )
    by_status = client.get(
        "/api/v1/route-cash-receipts?status=voided",
        headers=api_auth_headers,
    )
    filtered_paths = (
        f"?route_id={second_context['route_id']}",
        f"?vehicle_id={second_context['vehicle_id']}",
        f"?route_closure_id={second_context['closure_id']}",
        f"?cash_session_id={second_context['cash_session_id']}",
        f"?search={second_context['route_name']}",
    )
    filtered = [
        client.get(
            f"/api/v1/route-cash-receipts{path}",
            headers=api_auth_headers,
        )
        for path in filtered_paths
    ]
    after = client.get(
        f"/api/v1/route-closures/{second_context['closure_id']}/cash-receipt",
        headers=api_auth_headers,
    )

    assert before.json() == {"status": "not_received", "active_receipt": None}
    assert detail.status_code == 200
    assert detail.json()["id"] == second["id"]
    assert [item["id"] for item in by_date.json()] == [second["id"]]
    assert [item["id"] for item in by_status.json()] == [first["id"]]
    for response in filtered:
        assert [item["id"] for item in response.json()] == [second["id"]]
    assert after.json()["status"] == "received"
    assert after.json()["active_receipt"]["id"] == second["id"]


def test_cash_session_receipts_returns_history_and_active_totals(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    first_context = _seed_context(session_factory, "totals-a", day=18)
    second_context = _seed_context(
        session_factory,
        "totals-b",
        day=19,
        cash_session_id=first_context["cash_session_id"],
        delivered="40.00",
    )
    first = _create_receipt(
        client,
        api_auth_headers,
        first_context,
        received_amount="110.00",
    ).json()
    second = _create_receipt(
        client,
        api_auth_headers,
        second_context,
        received_amount="42.00",
    ).json()
    client.post(
        f"/api/v1/route-cash-receipts/{first['id']}/void",
        headers=api_auth_headers,
        json={"reason": "No debe sumar"},
    )

    response = client.get(
        f"/api/v1/cash-sessions/{first_context['cash_session_id']}"
        "/route-cash-receipts",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cash_session_id"] == first_context["cash_session_id"]
    assert {item["id"] for item in body["receipts"]} == {first["id"], second["id"]}
    assert body["totals"]["receipts_count"] == 1
    assert Decimal(body["totals"]["delivered_cash_total"]) == Decimal("40.00")
    assert Decimal(body["totals"]["received_amount_total"]) == Decimal("42.00")
    assert Decimal(body["totals"]["difference_total"]) == Decimal("2.00")


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("POST", "/api/v1/route-cash-receipts", {}),
        ("GET", "/api/v1/route-cash-receipts", None),
        ("GET", "/api/v1/route-cash-receipts/1", None),
        ("GET", "/api/v1/route-closures/1/cash-receipt", None),
        ("GET", "/api/v1/cash-sessions/1/route-cash-receipts", None),
        (
            "POST",
            "/api/v1/route-cash-receipts/1/void",
            {"reason": "Prueba"},
        ),
    ],
)
def test_route_cash_receipt_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_route_cash_receipts_migration(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0018_create_route_cash_receipts.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0018_route_cash_receipts",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[str] = []
    created_indexes: list[tuple[str, str, bool]] = []
    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda name, *args, **kwargs: created_tables.append(name),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda name, table, *args, **kwargs: created_indexes.append(
            (name, table, bool(kwargs.get("unique"))),
        ),
    )

    migration.upgrade()

    assert migration.revision == "0018_route_receipts"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0017_route_closures"
    assert created_tables == ["route_cash_receipts"]
    assert (
        "uq_route_cash_receipts_active_closure",
        "route_cash_receipts",
        True,
    ) in created_indexes


def _seed_context(
    session_factory,
    suffix: str,
    *,
    day: int = 18,
    closure_status: str = "active",
    cash_status: str = "open",
    cash_session_id: int | None = None,
    delivered: str = "115.00",
) -> dict[str, object]:
    with session_factory() as session:
        user = session.query(User).filter(User.username == "admin").one()
        route = DeliveryRoute(
            code=f"RCR-ROUTE-{suffix}",
            name=f"Ruta recibo {suffix}",
            expected_daily_cash=Decimal("0.00"),
        )
        vehicle = Vehicle(
            code=f"RCR-VEHICLE-{suffix}",
            name=f"Camion recibo {suffix}",
            vehicle_type="truck",
            fuel_type="diesel",
        )
        session.add_all([route, vehicle])
        session.flush()
        source = InventoryLocation(
            code=f"RCR-SOURCE-{suffix}",
            name=f"Bodega recibo {suffix}",
            location_type="warehouse",
        )
        destination = InventoryLocation(
            code=f"RCR-DEST-{suffix}",
            name=f"Vehiculo recibo {suffix}",
            location_type="vehicle",
            vehicle_id=vehicle.id,
        )
        session.add_all([source, destination])
        session.flush()
        route_load = RouteLoad(
            load_number=f"LOAD-RCR-{suffix}",
            load_date=date(2026, 7, day),
            route_id=route.id,
            vehicle_id=vehicle.id,
            source_location_id=source.id,
            destination_location_id=destination.id,
            status="active",
            created_by=user.id,
        )
        session.add(route_load)
        session.flush()
        voided_at = (
            datetime.now(timezone.utc) if closure_status == "voided" else None
        )
        closure = RouteClosure(
            closure_number=f"CLOSE-RCR-{suffix}",
            closure_date=date(2026, 7, day),
            route_load_id=route_load.id,
            route_id=route.id,
            vehicle_id=vehicle.id,
            load_number_snapshot=route_load.load_number,
            route_name_snapshot=route.name,
            vehicle_name_snapshot=vehicle.name,
            cash_sales_total=Decimal("0.00"),
            credit_sales_total=Decimal("0.00"),
            payments_total=Decimal("0.00"),
            expected_cash_total=Decimal("0.00"),
            delivered_cash_total=Decimal(delivered),
            difference_amount=Decimal(delivered),
            status=closure_status,
            void_reason="Cierre anulado" if closure_status == "voided" else None,
            voided_at=voided_at,
            created_by=user.id,
        )
        session.add(closure)
        session.flush()
        if cash_session_id is None:
            cash_session = CashSession(
                session_date=date(2026, 8, day),
                status=cash_status,
                closed_at=(
                    datetime.now(timezone.utc) if cash_status == "closed" else None
                ),
                created_by=user.id,
            )
            session.add(cash_session)
            session.flush()
            resolved_cash_session_id = cash_session.id
        else:
            resolved_cash_session_id = cash_session_id
        context = {
            "closure_id": closure.id,
            "cash_session_id": resolved_cash_session_id,
            "route_load_id": route_load.id,
            "route_id": route.id,
            "vehicle_id": vehicle.id,
            "closure_number": closure.closure_number,
            "route_name": route.name,
            "vehicle_name": vehicle.name,
        }
        session.commit()
        return context


def _create_receipt(
    client,
    headers,
    context: dict[str, object],
    *,
    receipt_date: str = "2026-07-18",
    received_amount: str | None = "115.00",
    notes: str | None = None,
):
    payload: dict[str, object] = {
        "receipt_date": receipt_date,
        "route_closure_id": context["closure_id"],
        "cash_session_id": context["cash_session_id"],
        "notes": notes,
    }
    if received_amount is not None:
        payload["received_amount"] = received_amount
    return client.post(
        "/api/v1/route-cash-receipts",
        headers=headers,
        json=payload,
    )


def _operational_counts(session) -> dict[str, int]:
    return {
        "cash_count_items": session.query(CashCountItem).count(),
        "expenses": session.query(Expense).count(),
        "inventory_movements": session.query(InventoryMovement).count(),
        "sales": session.query(Sale).count(),
        "credit_payments": session.query(CreditPayment).count(),
        "cash_sessions": session.query(CashSession).count(),
        "route_closures": session.query(RouteClosure).count(),
    }
