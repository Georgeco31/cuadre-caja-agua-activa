import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.route_closure import RouteClosure
from app.models.sale import Sale

CLOSED_MESSAGE = (
    "La carga ya tiene un cierre financiero activo. "
    "Primero anule el cierre financiero."
)


def test_create_route_closure_freezes_official_totals_and_snapshots(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    load_id = setup["load"]["id"]
    cash_sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
        quantity="2",
        unit_price="5.00",
    )
    credit_sale = _create_credit_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
        quantity="3",
        unit_price="4.00",
    )
    payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale.json()["id"],
        route_load_id=load_id,
        amount="4.00",
    )
    assert cash_sale.status_code == 201
    assert credit_sale.status_code == 201
    assert payment.status_code == 201

    response = _create_closure(
        client,
        api_auth_headers,
        load_id,
        delivered="11.00",
        notes="Faltante reportado",
    )

    assert response.status_code == 201, response.json()
    closure = response.json()
    assert closure["closure_number"].startswith("CLOSE-20260718-")
    assert closure["closure_date"] == "2026-07-18"
    assert closure["route_load_id"] == load_id
    assert closure["route_id"] == setup["route"]["id"]
    assert closure["vehicle_id"] == setup["vehicle"]["id"]
    assert closure["load_number_snapshot"] == setup["load"]["load_number"]
    assert closure["route_name_snapshot"] == setup["route"]["name"]
    assert closure["vehicle_name_snapshot"] == setup["vehicle"]["name"]
    assert Decimal(closure["cash_sales_total"]) == Decimal("10.00")
    assert Decimal(closure["credit_sales_total"]) == Decimal("12.00")
    assert Decimal(closure["payments_total"]) == Decimal("4.00")
    assert Decimal(closure["expected_cash_total"]) == Decimal("14.00")
    assert Decimal(closure["delivered_cash_total"]) == Decimal("11.00")
    assert Decimal(closure["difference_amount"]) == Decimal("-3.00")
    assert closure["status"] == "active"
    assert closure["notes"] == "Faltante reportado"


@pytest.mark.parametrize(
    ("delivered", "expected_difference"),
    [("5.00", "0.00"), ("7.50", "2.50"), ("2.00", "-3.00")],
)
def test_route_closure_calculates_balanced_surplus_and_shortage(
    api_client,
    api_auth_headers,
    delivered: str,
    expected_difference: str,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=setup["load"]["id"],
    )

    response = _create_closure(
        client,
        api_auth_headers,
        setup["load"]["id"],
        delivered=delivered,
    )

    assert response.status_code == 201
    assert Decimal(response.json()["expected_cash_total"]) == Decimal("5.00")
    assert Decimal(response.json()["difference_amount"]) == Decimal(
        expected_difference,
    )


def test_credit_sales_do_not_increase_expected_cash(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=setup["load"]["id"],
        quantity="4",
        unit_price="5.00",
    )

    closure = _create_closure(
        client,
        api_auth_headers,
        setup["load"]["id"],
        delivered="0",
    ).json()

    assert Decimal(closure["credit_sales_total"]) == Decimal("20.00")
    assert Decimal(closure["expected_cash_total"]) == Decimal("0.00")
    assert Decimal(closure["difference_amount"]) == Decimal("0.00")


def test_voided_sales_and_payments_are_excluded_from_closure(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    load_id = setup["load"]["id"]
    cash_sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
    ).json()
    credit_sale = _create_credit_sale(client, api_auth_headers, setup).json()
    payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale["id"],
        route_load_id=load_id,
    ).json()
    _void_sale(client, api_auth_headers, cash_sale["id"])
    _void_payment(client, api_auth_headers, payment["id"])

    closure = _create_closure(
        client,
        api_auth_headers,
        load_id,
        delivered="0",
    ).json()

    assert Decimal(closure["cash_sales_total"]) == Decimal("0.00")
    assert Decimal(closure["payments_total"]) == Decimal("0.00")
    assert Decimal(closure["expected_cash_total"]) == Decimal("0.00")


@pytest.mark.parametrize(
    "payload",
    [
        {"route_load_id": 1, "delivered_cash_total": "0"},
        {
            "closure_date": "2026-07-18",
            "route_load_id": 1,
            "delivered_cash_total": "-0.01",
        },
        {
            "closure_date": "2026-07-18",
            "route_load_id": 0,
            "delivered_cash_total": "0",
        },
    ],
)
def test_route_closure_rejects_invalid_payload(
    api_client,
    api_auth_headers,
    payload: dict[str, object],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/route-closures",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_route_closure_rejects_missing_or_voided_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)

    missing = _create_closure(client, api_auth_headers, 999)
    _void_load(client, api_auth_headers, setup["load"]["id"])
    voided = _create_closure(
        client,
        api_auth_headers,
        setup["load"]["id"],
    )

    assert missing.status_code == 404
    assert voided.status_code == 400
    assert "carga anulada" in voided.json()["detail"]


def test_only_one_active_closure_per_load_and_void_allows_replacement(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    load_id = setup["load"]["id"]
    first = _create_closure(client, api_auth_headers, load_id)
    duplicate = _create_closure(client, api_auth_headers, load_id)
    voided = _void_closure(client, api_auth_headers, first.json()["id"])
    replacement = _create_closure(client, api_auth_headers, load_id)

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    assert replacement.status_code == 201
    assert replacement.json()["id"] != first.json()["id"]


def test_list_detail_and_filters_route_closures(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_setup = _setup_route(client, api_auth_headers, suffix="A")
    second_setup = _setup_route(client, api_auth_headers, suffix="B")
    first = _create_closure(
        client,
        api_auth_headers,
        first_setup["load"]["id"],
        closure_date="2026-07-17",
    ).json()
    second = _create_closure(
        client,
        api_auth_headers,
        second_setup["load"]["id"],
        closure_date="2026-07-18",
    ).json()
    _void_closure(client, api_auth_headers, first["id"])

    all_response = client.get(
        "/api/v1/route-closures",
        headers=api_auth_headers,
    )
    detail = client.get(
        f"/api/v1/route-closures/{second['id']}",
        headers=api_auth_headers,
    )
    by_date = client.get(
        "/api/v1/route-closures?date_from=2026-07-18&date_to=2026-07-18",
        headers=api_auth_headers,
    )
    by_status = client.get(
        "/api/v1/route-closures?status=voided",
        headers=api_auth_headers,
    )
    by_route = client.get(
        f"/api/v1/route-closures?route_id={second_setup['route']['id']}",
        headers=api_auth_headers,
    )
    by_vehicle = client.get(
        f"/api/v1/route-closures?vehicle_id={second_setup['vehicle']['id']}",
        headers=api_auth_headers,
    )
    by_load = client.get(
        f"/api/v1/route-closures?route_load_id={second_setup['load']['id']}",
        headers=api_auth_headers,
    )
    search = client.get(
        f"/api/v1/route-closures?search={second_setup['route']['name']}",
        headers=api_auth_headers,
    )

    assert [item["id"] for item in all_response.json()] == [second["id"], first["id"]]
    assert detail.json()["id"] == second["id"]
    for response in (by_date, by_route, by_vehicle, by_load, search):
        assert [item["id"] for item in response.json()] == [second["id"]]
    assert [item["id"] for item in by_status.json()] == [first["id"]]


def test_financial_closure_status_for_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    load_id = setup["load"]["id"]

    before = client.get(
        f"/api/v1/route-loads/{load_id}/financial-closure",
        headers=api_auth_headers,
    )
    closure = _create_closure(client, api_auth_headers, load_id).json()
    after = client.get(
        f"/api/v1/route-loads/{load_id}/financial-closure",
        headers=api_auth_headers,
    )
    missing = client.get(
        "/api/v1/route-loads/999/financial-closure",
        headers=api_auth_headers,
    )

    assert before.json() == {"status": "not_closed", "active_closure": None}
    assert after.json()["status"] == "closed"
    assert after.json()["active_closure"]["id"] == closure["id"]
    assert missing.status_code == 404


def test_void_route_closure_requires_reason_and_is_not_repeatable(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_route(client, api_auth_headers)
    closure = _create_closure(
        client,
        api_auth_headers,
        setup["load"]["id"],
    ).json()

    missing_reason = client.post(
        f"/api/v1/route-closures/{closure['id']}/void",
        headers=api_auth_headers,
        json={},
    )
    blank_reason = client.post(
        f"/api/v1/route-closures/{closure['id']}/void",
        headers=api_auth_headers,
        json={"reason": "   "},
    )
    voided = _void_closure(client, api_auth_headers, closure["id"])
    repeated = _void_closure(client, api_auth_headers, closure["id"])

    assert missing_reason.status_code == 422
    assert blank_reason.status_code == 422
    assert voided.status_code == 200
    assert voided.json()["void_reason"] == "Cierre incorrecto"
    assert voided.json()["voided_at"] is not None
    assert repeated.status_code == 409
    with testing_session_local() as session:
        stored = session.get(RouteClosure, closure["id"])
        assert stored is not None
        assert stored.status == "voided"


def test_create_and_void_closure_do_not_modify_operational_records(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_route(client, api_auth_headers)
    load_id = setup["load"]["id"]
    sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
    ).json()
    credit_sale = _create_credit_sale(client, api_auth_headers, setup).json()
    payment = _create_payment(client, api_auth_headers, credit_sale["id"]).json()

    with testing_session_local() as session:
        before = _operational_snapshot(session, sale["id"], payment["id"])

    closure = _create_closure(client, api_auth_headers, load_id).json()
    _void_closure(client, api_auth_headers, closure["id"])

    with testing_session_local() as session:
        assert _operational_snapshot(session, sale["id"], payment["id"]) == before


def test_active_closure_blocks_load_sales_payments_and_voids(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    load_id = setup["load"]["id"]
    associated_sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
    ).json()
    credit_sale = _create_credit_sale(client, api_auth_headers, setup).json()
    associated_payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale["id"],
        route_load_id=load_id,
    ).json()
    _create_closure(client, api_auth_headers, load_id)

    blocked = [
        _create_cash_sale(
            client,
            api_auth_headers,
            setup,
            route_load_id=load_id,
        ),
        _create_credit_sale(
            client,
            api_auth_headers,
            setup,
            route_load_id=load_id,
        ),
        _create_payment(
            client,
            api_auth_headers,
            credit_sale["id"],
            route_load_id=load_id,
        ),
        client.post(
            f"/api/v1/sales/{associated_sale['id']}/void",
            headers=api_auth_headers,
            json={"reason": "Venta incorrecta"},
        ),
        client.post(
            f"/api/v1/credit-payments/{associated_payment['id']}/void",
            headers=api_auth_headers,
            json={"reason": "Pago incorrecto"},
        ),
        client.post(
            f"/api/v1/route-loads/{load_id}/void",
            headers=api_auth_headers,
            json={"reason": "Carga incorrecta"},
        ),
        _create_return(client, api_auth_headers, setup),
    ]

    for response in blocked:
        assert response.status_code == 409, response.json()
        assert response.json()["detail"] == CLOSED_MESSAGE


def test_active_closure_blocks_voiding_existing_return(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    route_return = _create_return(client, api_auth_headers, setup)
    assert route_return.status_code == 201, route_return.json()
    _create_closure(client, api_auth_headers, setup["load"]["id"])

    response = client.post(
        f"/api/v1/route-returns/{route_return.json()['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Retorno incorrecto"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == CLOSED_MESSAGE


def test_voided_closure_reopens_route_for_commercial_activity(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_route(client, api_auth_headers)
    closure = _create_closure(
        client,
        api_auth_headers,
        setup["load"]["id"],
    ).json()
    _void_closure(client, api_auth_headers, closure["id"])

    response = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=setup["load"]["id"],
    )

    assert response.status_code == 201, response.json()


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/route-closures",
            {
                "closure_date": "2026-07-18",
                "route_load_id": 1,
                "delivered_cash_total": "0",
            },
        ),
        ("GET", "/api/v1/route-closures", None),
        ("GET", "/api/v1/route-closures/1", None),
        ("GET", "/api/v1/route-loads/1/financial-closure", None),
        (
            "POST",
            "/api/v1/route-closures/1/void",
            {"reason": "Cierre incorrecto"},
        ),
    ],
)
def test_route_closure_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_route_closures_migration(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0017_create_route_closures.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0017_route_closures",
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

    assert migration.revision == "0017_route_closures"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0016_route_links"
    assert created_tables == ["route_closures"]
    assert ("ix_route_closures_route_load_id", "route_closures", False) in (
        created_indexes
    )
    assert (
        "uq_route_closures_active_route_load",
        "route_closures",
        True,
    ) in created_indexes


def _setup_route(client, headers, *, suffix: str = "01") -> dict:
    route = _post(
        client,
        "/api/v1/delivery-routes",
        headers,
        {
            "code": f"RUTA-CLOSE-{suffix}",
            "name": f"Ruta cierre {suffix}",
            "expected_daily_cash": "0",
        },
    )
    vehicle = _post(
        client,
        "/api/v1/vehicles",
        headers,
        {
            "code": f"CAM-CLOSE-{suffix}",
            "name": f"Camion cierre {suffix}",
            "vehicle_type": "truck",
            "fuel_type": "diesel",
        },
    )
    source = _post(
        client,
        "/api/v1/inventory/locations",
        headers,
        {
            "code": f"BOD-CLOSE-{suffix}",
            "name": f"Bodega cierre {suffix}",
            "location_type": "warehouse",
        },
    )
    destination = _post(
        client,
        "/api/v1/inventory/locations",
        headers,
        {
            "code": f"VEH-CLOSE-{suffix}",
            "name": f"Inventario camion cierre {suffix}",
            "location_type": "vehicle",
            "vehicle_id": vehicle["id"],
        },
    )
    product = _post(
        client,
        "/api/v1/products",
        headers,
        {
            "sku": f"PROD-CLOSE-{suffix}",
            "name": f"Producto cierre {suffix}",
            "category": "water",
            "unit": "container",
            "presentation": "20 L",
            "default_price": "5.00",
            "cost_estimate": "0.40",
        },
    )
    customer = _post(
        client,
        "/api/v1/customers",
        headers,
        {
            "name": f"Cliente cierre {suffix}",
            "customer_type": "business",
            "credit_allowed": True,
            "credit_limit": "1000.00",
        },
    )
    movement = client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "movement_date": "2026-07-18",
            "movement_type": "entry",
            "product_id": product["id"],
            "location_id": source["id"],
            "quantity": "100",
            "reason": "Stock controlado para cierre",
        },
    )
    assert movement.status_code == 201, movement.json()
    load = _post(
        client,
        "/api/v1/route-loads",
        headers,
        {
            "load_date": "2026-07-18",
            "route_id": route["id"],
            "vehicle_id": vehicle["id"],
            "source_location_id": source["id"],
            "destination_location_id": destination["id"],
            "items": [{"product_id": product["id"], "quantity_loaded": "20"}],
        },
    )
    return {
        "route": route,
        "vehicle": vehicle,
        "source": source,
        "destination": destination,
        "product": product,
        "customer": customer,
        "load": load,
    }


def _post(client, path: str, headers, payload: dict) -> dict:
    response = client.post(path, headers=headers, json=payload)
    assert response.status_code == 201, response.json()
    return response.json()


def _create_cash_sale(
    client,
    headers,
    setup: dict,
    *,
    route_load_id: int | None = None,
    quantity: str = "1",
    unit_price: str = "5.00",
):
    return client.post(
        "/api/v1/sales/cash",
        headers=headers,
        json={
            "sale_date": "2026-07-18",
            "customer_id": setup["customer"]["id"],
            "route_load_id": route_load_id,
            "payment_method": "cash",
            "items": [
                {
                    "product_id": setup["product"]["id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                }
            ],
        },
    )


def _create_credit_sale(
    client,
    headers,
    setup: dict,
    *,
    route_load_id: int | None = None,
    quantity: str = "1",
    unit_price: str = "5.00",
):
    return client.post(
        "/api/v1/sales/credit",
        headers=headers,
        json={
            "sale_date": "2026-07-18",
            "customer_id": setup["customer"]["id"],
            "route_load_id": route_load_id,
            "items": [
                {
                    "product_id": setup["product"]["id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                }
            ],
        },
    )


def _create_payment(
    client,
    headers,
    sale_id: int,
    *,
    route_load_id: int | None = None,
    amount: str = "1.00",
):
    return client.post(
        f"/api/v1/sales/{sale_id}/payments",
        headers=headers,
        json={
            "payment_date": "2026-07-18",
            "route_load_id": route_load_id,
            "amount": amount,
            "payment_method": "cash",
        },
    )


def _create_closure(
    client,
    headers,
    load_id: int,
    *,
    delivered: str = "0.00",
    closure_date: str = "2026-07-18",
    notes: str | None = None,
):
    return client.post(
        "/api/v1/route-closures",
        headers=headers,
        json={
            "closure_date": closure_date,
            "route_load_id": load_id,
            "delivered_cash_total": delivered,
            "notes": notes,
        },
    )


def _void_closure(client, headers, closure_id: int):
    return client.post(
        f"/api/v1/route-closures/{closure_id}/void",
        headers=headers,
        json={"reason": "Cierre incorrecto"},
    )


def _void_sale(client, headers, sale_id: int) -> None:
    response = client.post(
        f"/api/v1/sales/{sale_id}/void",
        headers=headers,
        json={"reason": "Venta incorrecta"},
    )
    assert response.status_code == 200, response.json()


def _void_payment(client, headers, payment_id: int) -> None:
    response = client.post(
        f"/api/v1/credit-payments/{payment_id}/void",
        headers=headers,
        json={"reason": "Pago incorrecto"},
    )
    assert response.status_code == 200, response.json()


def _void_load(client, headers, load_id: int) -> None:
    response = client.post(
        f"/api/v1/route-loads/{load_id}/void",
        headers=headers,
        json={"reason": "Carga incorrecta"},
    )
    assert response.status_code == 200, response.json()


def _create_return(client, headers, setup: dict):
    return client.post(
        "/api/v1/route-returns",
        headers=headers,
        json={
            "return_date": "2026-07-18",
            "route_load_id": setup["load"]["id"],
            "destination_location_id": setup["source"]["id"],
            "items": [
                {
                    "route_load_item_id": setup["load"]["items"][0]["id"],
                    "quantity_returned": "1",
                }
            ],
        },
    )


def _operational_snapshot(session, sale_id: int, payment_id: int) -> dict:
    sale = session.get(Sale, sale_id)
    payment = session.get(CreditPayment, payment_id)
    assert sale is not None
    assert payment is not None
    return {
        "cash_sessions": session.query(CashSession).count(),
        "movements": session.query(InventoryMovement).count(),
        "stocks": {
            (stock.product_id, stock.location_id): stock.quantity_on_hand
            for stock in session.query(InventoryStock).all()
        },
        "sale": (sale.status, sale.total_amount, sale.balance_amount),
        "payment": (payment.status, payment.amount),
    }
