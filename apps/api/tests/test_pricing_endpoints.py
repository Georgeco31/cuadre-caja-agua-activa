import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.inventory_movement import InventoryMovement
from app.models.price_list import PriceList
from app.models.price_list_item import PriceListItem
from app.models.sale_item import SaleItem


@pytest.mark.parametrize(
    ("list_type", "target_kind"),
    [
        ("general", None),
        ("customer", "customer"),
        ("route", "route"),
        ("customer_route", "both"),
    ],
)
def test_create_price_list_types(
    api_client,
    api_auth_headers,
    list_type: str,
    target_kind: str | None,
) -> None:
    client, _ = api_client
    customer = _create_customer(client, api_auth_headers)
    route = _create_route(client, api_auth_headers)
    payload = {
        "name": f"Lista {list_type}",
        "list_type": list_type,
        "priority": 10,
        "valid_from": "2026-07-01",
        "valid_to": "2026-07-31",
    }
    if target_kind in ("customer", "both"):
        payload["customer_id"] = customer["id"]
    if target_kind in ("route", "both"):
        payload["route_id"] = route["id"]

    response = client.post(
        "/api/v1/pricing/price-lists",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["list_type"] == list_type
    assert body["priority"] == 10
    assert body["is_active"] is True
    assert body["items"] == []


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Cliente incompleta", "list_type": "customer"},
        {"name": "Ruta incompleta", "list_type": "route"},
        {
            "name": "Combinada incompleta",
            "list_type": "customer_route",
            "customer_id": 1,
        },
    ],
)
def test_create_price_list_requires_its_target(
    api_client,
    api_auth_headers,
    payload: dict[str, object],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/pricing/price-lists",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_list_and_update_price_lists(api_client, api_auth_headers) -> None:
    client, _ = api_client
    expected = _create_price_list(
        client,
        api_auth_headers,
        name="Precio Tiendas",
        priority=3,
    )
    _create_price_list(client, api_auth_headers, name="Otra lista")

    response = client.get(
        "/api/v1/pricing/price-lists",
        headers=api_auth_headers,
        params={"search": "Tiendas", "list_type": "general", "is_active": True},
    )
    updated = client.patch(
        f"/api/v1/pricing/price-lists/{expected['id']}",
        headers=api_auth_headers,
        json={"name": "Precio Tiendas actualizado", "priority": 8},
    )

    assert [item["id"] for item in response.json()] == [expected["id"]]
    assert updated.status_code == 200
    assert updated.json()["name"] == "Precio Tiendas actualizado"
    assert updated.json()["priority"] == 8


def test_activate_and_deactivate_price_list(api_client, api_auth_headers) -> None:
    client, _ = api_client
    price_list = _create_price_list(client, api_auth_headers)

    deactivated = client.patch(
        f"/api/v1/pricing/price-lists/{price_list['id']}/deactivate",
        headers=api_auth_headers,
    )
    activated = client.patch(
        f"/api/v1/pricing/price-lists/{price_list['id']}/activate",
        headers=api_auth_headers,
    )

    assert deactivated.json()["is_active"] is False
    assert activated.json()["is_active"] is True


def test_add_and_update_price_list_item(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    price_list = _create_price_list(client, api_auth_headers)

    item = _add_item(
        client,
        api_auth_headers,
        price_list["id"],
        product["id"],
        unit_price="0.90",
        min_quantity="2",
    )
    updated = client.patch(
        f"/api/v1/pricing/price-list-items/{item['id']}",
        headers=api_auth_headers,
        json={"unit_price": "0.85", "min_quantity": "3"},
    )
    detail = client.get(
        f"/api/v1/pricing/price-lists/{price_list['id']}",
        headers=api_auth_headers,
    )

    assert item["product_name"] == product["name"]
    assert updated.json()["unit_price"] == "0.85"
    assert updated.json()["min_quantity"] == "3.000"
    assert detail.json()["items"][0]["id"] == item["id"]


@pytest.mark.parametrize(
    "payload",
    [
        {"product_id": 1, "unit_price": "-0.01", "min_quantity": "1"},
        {"product_id": 1, "unit_price": "1.00", "min_quantity": "0"},
    ],
)
def test_price_list_item_validates_decimal_values(
    api_client,
    api_auth_headers,
    payload: dict[str, object],
) -> None:
    client, _ = api_client
    price_list = _create_price_list(client, api_auth_headers)

    response = client.post(
        f"/api/v1/pricing/price-lists/{price_list['id']}/items",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_price_list_item_rejects_inactive_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    price_list = _create_price_list(client, api_auth_headers)
    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.post(
        f"/api/v1/pricing/price-lists/{price_list['id']}/items",
        headers=api_auth_headers,
        json={
            "product_id": product["id"],
            "unit_price": "0.80",
            "min_quantity": "1",
        },
    )

    assert response.status_code == 400
    assert "esta inactivo" in response.json()["detail"]


def test_activate_and_deactivate_price_list_item(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    price_list = _create_price_list(client, api_auth_headers)
    item = _add_item(
        client,
        api_auth_headers,
        price_list["id"],
        product["id"],
    )

    deactivated = client.patch(
        f"/api/v1/pricing/price-list-items/{item['id']}/deactivate",
        headers=api_auth_headers,
    )
    activated = client.patch(
        f"/api/v1/pricing/price-list-items/{item['id']}/activate",
        headers=api_auth_headers,
    )

    assert deactivated.json()["is_active"] is False
    assert activated.json()["is_active"] is True


def test_resolve_uses_default_price_without_list(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers, default_price="1.25")

    body = _resolve(client, api_auth_headers, product["id"])

    assert body["default_price"] == "1.25"
    assert body["resolved_price"] == "1.25"
    assert body["price_source"] == "default"
    assert body["price_list_id"] is None


def test_resolve_customer_price_over_general(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    customer = _create_customer(client, api_auth_headers)
    general = _create_price_list(client, api_auth_headers, name="General")
    customer_list = _create_price_list(
        client,
        api_auth_headers,
        name="Cliente",
        list_type="customer",
        customer_id=customer["id"],
    )
    _add_item(
        client,
        api_auth_headers,
        general["id"],
        product["id"],
        unit_price="0.95",
    )
    _add_item(
        client,
        api_auth_headers,
        customer_list["id"],
        product["id"],
        unit_price="0.90",
    )

    body = _resolve(
        client,
        api_auth_headers,
        product["id"],
        customer_id=customer["id"],
    )

    assert body["resolved_price"] == "0.90"
    assert body["price_source"] == "customer"
    assert body["price_list_name"] == "Cliente"


def test_resolve_route_price(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    route = _create_route(client, api_auth_headers)
    route_list = _create_price_list(
        client,
        api_auth_headers,
        list_type="route",
        route_id=route["id"],
    )
    _add_item(
        client,
        api_auth_headers,
        route_list["id"],
        product["id"],
        unit_price="0.95",
    )

    body = _resolve(
        client,
        api_auth_headers,
        product["id"],
        route_id=route["id"],
    )

    assert body["resolved_price"] == "0.95"
    assert body["price_source"] == "route"


def test_resolve_customer_route_over_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    customer = _create_customer(client, api_auth_headers)
    route = _create_route(client, api_auth_headers)
    customer_list = _create_price_list(
        client,
        api_auth_headers,
        list_type="customer",
        customer_id=customer["id"],
        priority=100,
    )
    combined = _create_price_list(
        client,
        api_auth_headers,
        list_type="customer_route",
        customer_id=customer["id"],
        route_id=route["id"],
        priority=0,
    )
    _add_item(
        client,
        api_auth_headers,
        customer_list["id"],
        product["id"],
        unit_price="0.90",
    )
    _add_item(
        client,
        api_auth_headers,
        combined["id"],
        product["id"],
        unit_price="0.85",
    )

    body = _resolve(
        client,
        api_auth_headers,
        product["id"],
        customer_id=customer["id"],
        route_id=route["id"],
    )

    assert body["resolved_price"] == "0.85"
    assert body["price_source"] == "customer_route"


def test_resolve_prefers_priority_with_same_specificity(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    low = _create_price_list(client, api_auth_headers, priority=1)
    high = _create_price_list(client, api_auth_headers, priority=20)
    _add_item(
        client,
        api_auth_headers,
        low["id"],
        product["id"],
        unit_price="0.95",
    )
    _add_item(
        client,
        api_auth_headers,
        high["id"],
        product["id"],
        unit_price="0.80",
    )

    body = _resolve(client, api_auth_headers, product["id"])

    assert body["resolved_price"] == "0.80"
    assert body["price_list_id"] == high["id"]


@pytest.mark.parametrize("inactive_kind", ["list", "item"])
def test_resolve_ignores_inactive_prices(
    api_client,
    api_auth_headers,
    inactive_kind: str,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers, default_price="1.00")
    price_list = _create_price_list(client, api_auth_headers)
    item = _add_item(
        client,
        api_auth_headers,
        price_list["id"],
        product["id"],
        unit_price="0.50",
    )
    path = (
        f"/api/v1/pricing/price-lists/{price_list['id']}/deactivate"
        if inactive_kind == "list"
        else f"/api/v1/pricing/price-list-items/{item['id']}/deactivate"
    )
    client.patch(path, headers=api_auth_headers)

    body = _resolve(client, api_auth_headers, product["id"])

    assert body["resolved_price"] == "1.00"
    assert body["price_source"] == "default"


def test_resolve_ignores_out_of_date_list(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    price_list = _create_price_list(
        client,
        api_auth_headers,
        valid_from="2026-08-01",
        valid_to="2026-08-31",
    )
    _add_item(
        client,
        api_auth_headers,
        price_list["id"],
        product["id"],
        unit_price="0.50",
    )

    body = _resolve(client, api_auth_headers, product["id"])

    assert body["resolved_price"] == "1.00"


def test_resolve_honors_minimum_quantity(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    price_list = _create_price_list(client, api_auth_headers)
    _add_item(
        client,
        api_auth_headers,
        price_list["id"],
        product["id"],
        unit_price="0.70",
        min_quantity="10",
    )

    below = _resolve(client, api_auth_headers, product["id"], quantity="9")
    applicable = _resolve(
        client,
        api_auth_headers,
        product["id"],
        quantity="10",
    )

    assert below["resolved_price"] == "1.00"
    assert applicable["resolved_price"] == "0.70"


def test_cash_sale_resolves_price_and_keeps_manual_compatibility(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    customer = _create_customer(client, api_auth_headers)
    price_list = _create_price_list(
        client,
        api_auth_headers,
        name="Precio Cliente",
        list_type="customer",
        customer_id=customer["id"],
    )
    _add_item(
        client,
        api_auth_headers,
        price_list["id"],
        product["id"],
        unit_price="0.90",
    )

    automatic = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-24",
            "customer_id": customer["id"],
            "items": [{"product_id": product["id"], "quantity": "2"}],
        },
    )
    manual = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-24",
            "customer_id": customer["id"],
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": "1",
                    "unit_price": "0.75",
                }
            ],
        },
    )

    assert automatic.status_code == 201, automatic.text
    assert automatic.json()["total_amount"] == "1.80"
    assert automatic.json()["items"][0]["price_source"] == "customer"
    assert automatic.json()["items"][0]["price_list_id"] == price_list["id"]
    assert (
        automatic.json()["items"][0]["price_list_name_snapshot"]
        == "Precio Cliente"
    )
    assert manual.status_code == 201
    assert manual.json()["items"][0]["unit_price"] == "0.75"
    assert manual.json()["items"][0]["price_source"] == "manual"
    with testing_session_local() as session:
        assert session.query(CashSession).count() == 0
        assert session.query(InventoryMovement).count() == 0


def test_credit_sale_uses_resolved_price_and_balance(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    customer = _create_customer(
        client,
        api_auth_headers,
        credit_allowed=True,
        credit_limit="100.00",
    )
    price_list = _create_price_list(
        client,
        api_auth_headers,
        list_type="customer",
        customer_id=customer["id"],
    )
    _add_item(
        client,
        api_auth_headers,
        price_list["id"],
        product["id"],
        unit_price="0.80",
    )

    response = client.post(
        "/api/v1/sales/credit",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-24",
            "customer_id": customer["id"],
            "items": [{"product_id": product["id"], "quantity": "3"}],
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["total_amount"] == "2.40"
    assert response.json()["balance_amount"] == "2.40"
    assert response.json()["items"][0]["price_source"] == "customer"


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        (
            "POST",
            "/api/v1/pricing/price-lists",
            {"name": "Lista", "list_type": "general"},
        ),
        ("GET", "/api/v1/pricing/price-lists", None),
        ("GET", "/api/v1/pricing/price-lists/1", None),
        ("PATCH", "/api/v1/pricing/price-lists/1", {"name": "Lista"}),
        ("PATCH", "/api/v1/pricing/price-lists/1/deactivate", None),
        (
            "POST",
            "/api/v1/pricing/price-lists/1/items",
            {"product_id": 1, "unit_price": "1.00"},
        ),
        ("PATCH", "/api/v1/pricing/price-list-items/1", {"unit_price": "1"}),
        ("GET", "/api/v1/pricing/resolve?product_id=1", None),
    ],
)
def test_pricing_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_pricing_migration_creates_tables_and_traceability(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0020_create_price_lists.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0020_price_lists",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[str] = []
    created_indexes: list[str] = []
    added_columns: list[str] = []

    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *args, **kwargs: created_tables.append(table_name),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda index_name, *args, **kwargs: created_indexes.append(index_name),
    )
    monkeypatch.setattr(
        migration.op,
        "add_column",
        lambda table_name, column: added_columns.append(column.name),
    )
    monkeypatch.setattr(
        migration.op,
        "create_check_constraint",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        migration.op,
        "create_foreign_key",
        lambda *args, **kwargs: None,
    )

    migration.upgrade()

    assert migration.revision == "0020_price_lists"
    assert migration.down_revision == "0019_purchases"
    assert len(migration.revision) <= 32
    assert created_tables == ["price_lists", "price_list_items"]
    assert {
        "ix_price_lists_list_type",
        "ix_price_list_items_product_id",
        "ix_sale_items_price_list_id",
    } <= set(created_indexes)
    assert added_columns == [
        "price_source",
        "price_list_id",
        "price_list_name_snapshot",
        "pricing_note",
    ]


def test_pricing_does_not_create_fake_data(api_client) -> None:
    _, testing_session_local = api_client

    with testing_session_local() as session:
        assert session.query(PriceList).count() == 0
        assert session.query(PriceListItem).count() == 0
        assert session.query(SaleItem).count() == 0


def _create_customer(client, headers, **overrides):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": "Cliente Especial", **overrides},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_route(client, headers):
    response = client.post(
        "/api/v1/delivery-routes",
        headers=headers,
        json={"code": "CENTRO", "name": "Ruta Centro"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_product(client, headers, **overrides):
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": "BIDON-20L",
            "name": "Bidon 20L",
            "default_price": "1.00",
            **overrides,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_price_list(client, headers, **overrides):
    response = client.post(
        "/api/v1/pricing/price-lists",
        headers=headers,
        json={
            "name": "Lista de precios",
            "list_type": "general",
            **overrides,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _add_item(
    client,
    headers,
    price_list_id: int,
    product_id: int,
    **overrides,
):
    response = client.post(
        f"/api/v1/pricing/price-lists/{price_list_id}/items",
        headers=headers,
        json={
            "product_id": product_id,
            "unit_price": "0.90",
            "min_quantity": "1",
            **overrides,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _resolve(client, headers, product_id: int, **params):
    response = client.get(
        "/api/v1/pricing/resolve",
        headers=headers,
        params={
            "product_id": product_id,
            "price_date": "2026-07-24",
            **params,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()
