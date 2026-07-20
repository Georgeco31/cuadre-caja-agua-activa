import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.route_load import RouteLoad
from app.models.route_return import RouteReturn
from app.models.sale import Sale


def test_commercial_records_without_route_load_remain_supported(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)

    cash_sale = _create_cash_sale(client, api_auth_headers, setup)
    credit_sale = _create_credit_sale(client, api_auth_headers, setup)
    payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale.json()["id"],
        amount="2",
    )

    assert cash_sale.status_code == 201
    assert credit_sale.status_code == 201
    assert payment.status_code == 201
    for record in (cash_sale.json(), credit_sale.json(), payment.json()):
        assert record["route_load_id"] is None
        assert record["route_load_number"] is None
        assert record["route_name"] is None
        assert record["route_vehicle_name"] is None


def test_create_cash_credit_and_payment_with_route_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    load_id = setup["load"]["id"]

    cash_sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
    )
    credit_sale = _create_credit_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
    )
    payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale.json()["id"],
        route_load_id=load_id,
    )

    for response in (cash_sale, credit_sale, payment):
        assert response.status_code == 201, response.json()
        record = response.json()
        assert record["route_load_id"] == load_id
        assert record["route_load_number"] == setup["load"]["load_number"]
        assert record["route_name"] == setup["route"]["name"]
        assert record["route_vehicle_name"] == setup["vehicle"]["name"]
        assert record["route_load_status"] == "active"


@pytest.mark.parametrize("sale_type", ["cash", "credit"])
def test_sale_rejects_missing_or_voided_route_load(
    api_client,
    api_auth_headers,
    sale_type: str,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    create_sale = _create_cash_sale if sale_type == "cash" else _create_credit_sale

    missing = create_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=999,
    )
    _void_load(client, api_auth_headers, setup["load"]["id"])
    voided = create_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=setup["load"]["id"],
    )

    assert missing.status_code == 404
    assert voided.status_code == 400
    assert "carga anulada" in voided.json()["detail"]


def test_payment_rejects_missing_or_voided_route_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    first_credit_sale = _create_credit_sale(client, api_auth_headers, setup).json()
    second_credit_sale = _create_credit_sale(client, api_auth_headers, setup).json()

    missing = _create_payment(
        client,
        api_auth_headers,
        first_credit_sale["id"],
        route_load_id=999,
    )
    _void_load(client, api_auth_headers, setup["load"]["id"])
    voided = _create_payment(
        client,
        api_auth_headers,
        second_credit_sale["id"],
        route_load_id=setup["load"]["id"],
    )

    assert missing.status_code == 404
    assert voided.status_code == 400
    assert "carga anulada" in voided.json()["detail"]


def test_sales_and_payments_can_be_filtered_by_route_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first = _setup_commercial_route(client, api_auth_headers, suffix="A")
    second = _setup_commercial_route(client, api_auth_headers, suffix="B")
    first_sale = _create_credit_sale(
        client,
        api_auth_headers,
        first,
        route_load_id=first["load"]["id"],
    ).json()
    second_sale = _create_credit_sale(
        client,
        api_auth_headers,
        second,
        route_load_id=second["load"]["id"],
    ).json()
    first_payment = _create_payment(
        client,
        api_auth_headers,
        first_sale["id"],
        route_load_id=first["load"]["id"],
    ).json()
    _create_payment(
        client,
        api_auth_headers,
        second_sale["id"],
        route_load_id=second["load"]["id"],
    )

    sales_response = client.get(
        f"/api/v1/sales?route_load_id={first['load']['id']}",
        headers=api_auth_headers,
    )
    payments_response = client.get(
        f"/api/v1/credit-payments?route_load_id={first['load']['id']}",
        headers=api_auth_headers,
    )
    sale_detail = client.get(
        f"/api/v1/sales/{first_sale['id']}",
        headers=api_auth_headers,
    )

    assert [sale["id"] for sale in sales_response.json()] == [first_sale["id"]]
    assert [payment["id"] for payment in payments_response.json()] == [
        first_payment["id"],
    ]
    assert sale_detail.json()["route_load_id"] == first["load"]["id"]


def test_route_commercial_activity_calculates_totals_and_groups_products(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    load_id = setup["load"]["id"]
    cash_sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
        quantity="2",
        unit_price="5.00",
    ).json()
    credit_sale = _create_credit_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
        quantity="3",
        unit_price="4.00",
    ).json()
    payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale["id"],
        route_load_id=load_id,
        amount="4.00",
    ).json()

    response = client.get(
        f"/api/v1/route-loads/{load_id}/commercial-activity",
        headers=api_auth_headers,
    )

    assert response.status_code == 200, response.json()
    activity = response.json()
    assert activity["load_number"] == setup["load"]["load_number"]
    assert activity["route_name"] == setup["route"]["name"]
    assert activity["vehicle_name"] == setup["vehicle"]["name"]
    assert [sale["id"] for sale in activity["cash_sales"]] == [cash_sale["id"]]
    assert [sale["id"] for sale in activity["credit_sales"]] == [
        credit_sale["id"],
    ]
    assert [item["id"] for item in activity["payments"]] == [payment["id"]]
    assert Decimal(activity["cash_sales_total"]) == Decimal("10.00")
    assert Decimal(activity["credit_sales_total"]) == Decimal("12.00")
    assert Decimal(activity["payments_total"]) == Decimal("4.00")
    assert Decimal(activity["expected_cash_total"]) == Decimal("14.00")
    assert activity["products_sold"] == [
        {
            "product_id": setup["product"]["id"],
            "product_name_snapshot": setup["product"]["name"],
            "total_quantity": "5.000",
            "total_amount": "22.00",
        }
    ]


def test_route_commercial_activity_excludes_voided_records(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
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

    response = client.get(
        f"/api/v1/route-loads/{load_id}/commercial-activity",
        headers=api_auth_headers,
    )

    activity = response.json()
    assert activity["cash_sales"] == []
    assert activity["credit_sales"] == []
    assert activity["payments"] == []
    assert Decimal(activity["expected_cash_total"]) == Decimal("0.00")
    assert activity["products_sold"] == []


def test_route_linked_sales_and_payment_do_not_modify_inventory_or_cash(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    load_id = setup["load"]["id"]
    with testing_session_local() as session:
        movement_count = session.query(InventoryMovement).count()
        stock_rows = {
            (stock.product_id, stock.location_id): stock.quantity_on_hand
            for stock in session.query(InventoryStock).all()
        }
        cash_session_count = session.query(CashSession).count()

    cash_sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
    )
    credit_sale = _create_credit_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=load_id,
    )
    payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale.json()["id"],
        route_load_id=load_id,
    )
    assert cash_sale.status_code == 201
    assert credit_sale.status_code == 201
    assert payment.status_code == 201

    with testing_session_local() as session:
        assert session.query(InventoryMovement).count() == movement_count
        assert {
            (stock.product_id, stock.location_id): stock.quantity_on_hand
            for stock in session.query(InventoryStock).all()
        } == stock_rows
        assert session.query(CashSession).count() == cash_session_count
        assert session.query(RouteReturn).count() == 0
        stored_load = session.get(RouteLoad, load_id)
        assert stored_load is not None
        assert stored_load.status == "active"


def test_route_load_cannot_be_voided_with_active_sale(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=setup["load"]["id"],
    )

    response = _void_load_response(client, api_auth_headers, setup["load"]["id"])

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "No se puede anular la carga porque tiene ventas o cobros asociados."
    )


def test_route_load_cannot_be_voided_with_active_payment(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    credit_sale = _create_credit_sale(client, api_auth_headers, setup).json()
    _create_payment(
        client,
        api_auth_headers,
        credit_sale["id"],
        route_load_id=setup["load"]["id"],
    )

    response = _void_load_response(client, api_auth_headers, setup["load"]["id"])

    assert response.status_code == 400
    assert "ventas o cobros asociados" in response.json()["detail"]


def test_voided_sale_does_not_block_route_load_void(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    sale = _create_cash_sale(
        client,
        api_auth_headers,
        setup,
        route_load_id=setup["load"]["id"],
    ).json()
    _void_sale(client, api_auth_headers, sale["id"])

    response = _void_load_response(client, api_auth_headers, setup["load"]["id"])

    assert response.status_code == 200, response.json()


def test_voided_payment_does_not_block_route_load_void(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_commercial_route(client, api_auth_headers)
    credit_sale = _create_credit_sale(client, api_auth_headers, setup).json()
    payment = _create_payment(
        client,
        api_auth_headers,
        credit_sale["id"],
        route_load_id=setup["load"]["id"],
    ).json()
    _void_payment(client, api_auth_headers, payment["id"])

    response = _void_load_response(client, api_auth_headers, setup["load"]["id"])

    assert response.status_code == 200, response.json()


def test_route_commercial_activity_requires_existing_load_and_authentication(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    missing = client.get(
        "/api/v1/route-loads/999/commercial-activity",
        headers=api_auth_headers,
    )
    unauthenticated = client.get(
        "/api/v1/route-loads/1/commercial-activity",
    )

    assert missing.status_code == 404
    assert unauthenticated.status_code == 401


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/sales/cash",
            {
                "sale_date": "2026-07-18",
                "route_load_id": 1,
                "items": [{"product_id": 1, "quantity": "1"}],
            },
        ),
        (
            "POST",
            "/api/v1/sales/1/payments",
            {
                "payment_date": "2026-07-18",
                "route_load_id": 1,
                "amount": "1",
                "payment_method": "cash",
            },
        ),
        ("GET", "/api/v1/sales?route_load_id=1", None),
        ("GET", "/api/v1/credit-payments?route_load_id=1", None),
    ],
)
def test_route_commercial_link_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_route_commercial_links_migration(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0016_route_commercial_links.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0016_route_links",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    added_columns: list[tuple[str, str]] = []
    created_indexes: list[tuple[str, str]] = []
    monkeypatch.setattr(
        migration.op,
        "add_column",
        lambda table, column: added_columns.append((table, column.name)),
    )
    monkeypatch.setattr(
        migration.op,
        "create_foreign_key",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda name, table, *args, **kwargs: created_indexes.append((name, table)),
    )

    migration.upgrade()

    assert migration.revision == "0016_route_links"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0015_route_returns"
    assert added_columns == [
        ("sales", "route_load_id"),
        ("credit_payments", "route_load_id"),
    ]
    assert created_indexes == [
        ("ix_sales_route_load_id", "sales"),
        ("ix_credit_payments_route_load_id", "credit_payments"),
    ]


def _setup_commercial_route(
    client,
    headers,
    *,
    suffix: str = "01",
) -> dict:
    route = _create_route(client, headers, code=f"RUTA-COM-{suffix}")
    vehicle = _create_vehicle(client, headers, code=f"CAM-COM-{suffix}")
    warehouse = _create_location(
        client,
        headers,
        code=f"BOD-COM-{suffix}",
        name=f"Bodega comercial {suffix}",
    )
    vehicle_location = _create_location(
        client,
        headers,
        code=f"VEH-COM-{suffix}",
        name=f"Inventario camion comercial {suffix}",
        location_type="vehicle",
        vehicle_id=vehicle["id"],
    )
    product = _create_product(client, headers, sku=f"PROD-COM-{suffix}")
    customer = _create_customer(client, headers, name=f"Cliente comercial {suffix}")
    stock = _create_movement(
        client,
        headers,
        product["id"],
        warehouse["id"],
        quantity="100",
    )
    assert stock.status_code == 201, stock.json()
    load_response = client.post(
        "/api/v1/route-loads",
        headers=headers,
        json={
            "load_date": "2026-07-18",
            "route_id": route["id"],
            "vehicle_id": vehicle["id"],
            "source_location_id": warehouse["id"],
            "destination_location_id": vehicle_location["id"],
            "items": [{"product_id": product["id"], "quantity_loaded": "20"}],
        },
    )
    assert load_response.status_code == 201, load_response.json()
    return {
        "route": route,
        "vehicle": vehicle,
        "warehouse": warehouse,
        "vehicle_location": vehicle_location,
        "product": product,
        "customer": customer,
        "load": load_response.json(),
    }


def _create_route(client, headers, *, code: str) -> dict:
    response = client.post(
        "/api/v1/delivery-routes",
        headers=headers,
        json={"code": code, "name": f"Ruta {code}", "expected_daily_cash": "0"},
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_vehicle(client, headers, *, code: str) -> dict:
    response = client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "code": code,
            "name": f"Vehiculo {code}",
            "vehicle_type": "truck",
            "fuel_type": "diesel",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_location(
    client,
    headers,
    *,
    code: str,
    name: str,
    location_type: str = "warehouse",
    vehicle_id: int | None = None,
) -> dict:
    response = client.post(
        "/api/v1/inventory/locations",
        headers=headers,
        json={
            "code": code,
            "name": name,
            "location_type": location_type,
            "vehicle_id": vehicle_id,
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_product(client, headers, *, sku: str) -> dict:
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": sku,
            "name": f"Producto {sku}",
            "category": "water",
            "unit": "container",
            "presentation": "20 L",
            "default_price": "5.00",
            "cost_estimate": "0.40",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_customer(client, headers, *, name: str) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": name,
            "customer_type": "business",
            "credit_allowed": True,
            "credit_limit": "1000.00",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_movement(client, headers, product_id: int, location_id: int, *, quantity: str):
    return client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "movement_date": "2026-07-18",
            "movement_type": "entry",
            "product_id": product_id,
            "location_id": location_id,
            "quantity": quantity,
            "reason": "Stock inicial controlado",
        },
    )


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


def _void_sale(client, headers, sale_id: int) -> dict:
    response = client.post(
        f"/api/v1/sales/{sale_id}/void",
        headers=headers,
        json={"reason": "Venta incorrecta"},
    )
    assert response.status_code == 200, response.json()
    return response.json()


def _void_payment(client, headers, payment_id: int) -> dict:
    response = client.post(
        f"/api/v1/credit-payments/{payment_id}/void",
        headers=headers,
        json={"reason": "Pago incorrecto"},
    )
    assert response.status_code == 200, response.json()
    return response.json()


def _void_load_response(client, headers, load_id: int):
    return client.post(
        f"/api/v1/route-loads/{load_id}/void",
        headers=headers,
        json={"reason": "Carga incorrecta"},
    )


def _void_load(client, headers, load_id: int) -> dict:
    response = _void_load_response(client, headers, load_id)
    assert response.status_code == 200, response.json()
    return response.json()
