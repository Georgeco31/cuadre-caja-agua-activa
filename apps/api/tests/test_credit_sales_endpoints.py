import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


def test_create_credit_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)

    body = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        due_date="2026-07-31",
        notes="Credito para tienda",
    )

    assert body["sale_number"].startswith("SALE-20260718-")
    assert body["sale_type"] == "credit"
    assert body["customer_id"] == customer["id"]
    assert body["customer_name_snapshot"] == customer["name"]
    assert body["due_date"] == "2026-07-31"
    assert body["notes"] == "Credito para tienda"


def test_create_credit_sale_requires_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = client.post(
        "/api/v1/sales/credit",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-18",
            "items": [{"product_id": product["id"], "quantity": "1"}],
        },
    )

    assert response.status_code == 422


def test_create_credit_sale_rejects_missing_customer(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = _credit_sale_response(
        client,
        api_auth_headers,
        999,
        product["id"],
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El cliente no existe."


def test_create_credit_sale_rejects_inactive_customer(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    client.patch(
        f"/api/v1/customers/{customer['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "El cliente esta inactivo."


def test_create_credit_sale_rejects_customer_without_credit(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(
        client,
        api_auth_headers,
        credit_allowed=False,
    )
    product = _create_product(client, api_auth_headers)

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "El cliente no tiene credito permitido."


def test_create_credit_sale_enforces_credit_limit(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(
        client,
        api_auth_headers,
        credit_limit="5.00",
    )
    product = _create_product(client, api_auth_headers)

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="6",
    )

    assert response.status_code == 400
    assert "supera el limite de credito" in response.json()["detail"]
    assert "5.00" in response.json()["detail"]


def test_credit_limit_includes_existing_active_debt(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(
        client,
        api_auth_headers,
        credit_limit="10.00",
    )
    product = _create_product(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="6",
    )

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="5",
    )

    assert response.status_code == 400
    assert "4.00" in response.json()["detail"]


def test_credit_limit_zero_means_no_defined_limit(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(
        client,
        api_auth_headers,
        credit_limit="0.00",
    )
    product = _create_product(client, api_auth_headers)

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="1000",
    )

    assert response.status_code == 201
    assert response.json()["total_amount"] == "1000.00"


def test_voided_credit_releases_customer_limit(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(
        client,
        api_auth_headers,
        credit_limit="10.00",
    )
    product = _create_product(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="10",
    )
    client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Venta anulada"},
    )

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="10",
    )

    assert response.status_code == 201


def test_create_credit_sale_with_multiple_products(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    first = _create_product(client, api_auth_headers)
    second = _create_product(
        client,
        api_auth_headers,
        name="Botella 500ml",
        sku="BOT-500",
        default_price="0.50",
    )

    body = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        items=[
            {"product_id": first["id"], "quantity": "2"},
            {"product_id": second["id"], "quantity": "4"},
        ],
    )

    assert len(body["items"]) == 2
    assert body["total_amount"] == "4.00"


def test_create_credit_sale_uses_default_price(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers, default_price="1.35")

    body = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    assert body["items"][0]["unit_price"] == "1.35"


def test_create_credit_sale_calculates_subtotal(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)

    body = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        items=[
            {"product_id": product["id"], "quantity": "2.5", "unit_price": "1.20"}
        ],
    )

    assert body["items"][0]["subtotal"] == "3.00"


def test_credit_sale_amounts_are_set_by_backend(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)

    body = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="3",
    )

    assert body["total_amount"] == "3.00"
    assert body["paid_amount"] == "0.00"
    assert body["balance_amount"] == "3.00"
    assert body["credit_status"] == "pending"


def test_create_credit_sale_requires_items(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)

    response = client.post(
        "/api/v1/sales/credit",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-18",
            "customer_id": customer["id"],
            "items": [],
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("quantity", ["0", "-1"])
def test_create_credit_sale_rejects_nonpositive_quantity(
    api_client,
    api_auth_headers,
    quantity: str,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity=quantity,
    )

    assert response.status_code == 422


def test_create_credit_sale_rejects_negative_price(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        unit_price="-0.01",
    )

    assert response.status_code == 422


def test_create_credit_sale_rejects_missing_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        999,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El producto 999 no existe."


def test_create_credit_sale_rejects_inactive_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = _credit_sale_response(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    assert response.status_code == 400
    assert "esta inactivo" in response.json()["detail"]


def test_list_sales_filters_credit_sales(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    credit_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    _create_cash_sale(client, api_auth_headers, product["id"])

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"sale_type": "credit"},
    )

    assert response.status_code == 200
    assert [sale["id"] for sale in response.json()] == [credit_sale["id"]]


def test_list_sales_filters_cash_sales(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    cash_sale = _create_cash_sale(client, api_auth_headers, product["id"])

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"sale_type": "cash"},
    )

    assert response.status_code == 200
    assert [sale["id"] for sale in response.json()] == [cash_sale["id"]]


def test_get_credit_sale_detail(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    response = client.get(
        f"/api/v1/sales/{sale['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == sale


def test_void_credit_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    response = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": " Error de registro "},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "voided"
    assert body["credit_status"] == "voided"
    assert body["balance_amount"] == "0.00"
    assert body["void_reason"] == "Error de registro"
    assert body["voided_at"] is not None


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_credit_sale_requires_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    response = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_void_credit_sale_cannot_be_repeated(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Primer motivo"},
    )

    response = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Segundo motivo"},
    )

    assert response.status_code == 409


def test_void_credit_sale_preserves_sale_items(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Anulacion controlada"},
    )

    with testing_session_local() as session:
        stored_sale = session.get(Sale, sale["id"])
        stored_items = session.query(SaleItem).filter_by(sale_id=sale["id"]).all()

    assert stored_sale is not None
    assert len(stored_items) == 1


def test_get_customer_credit_balance(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="10",
    )
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="5",
    )

    response = client.get(
        f"/api/v1/sales/credit/customer/{customer['id']}/balance",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "customer_id": customer["id"],
        "customer_name": customer["name"],
        "total_credit_sales": "15.00",
        "total_paid": "0.00",
        "total_balance": "15.00",
    }


def test_customer_balance_excludes_cash_sales(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    _create_cash_sale(
        client,
        api_auth_headers,
        product["id"],
        customer_id=customer["id"],
    )

    balance = client.get(
        f"/api/v1/sales/credit/customer/{customer['id']}/balance",
        headers=api_auth_headers,
    ).json()

    assert balance["total_credit_sales"] == "0.00"
    assert balance["total_balance"] == "0.00"


def test_customer_balance_excludes_voided_credit_sales(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "No debe contar"},
    )

    balance = client.get(
        f"/api/v1/sales/credit/customer/{customer['id']}/balance",
        headers=api_auth_headers,
    ).json()

    assert balance["total_credit_sales"] == "0.00"
    assert balance["total_balance"] == "0.00"


def test_customer_balance_returns_404_for_missing_customer(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/sales/credit/customer/999/balance",
        headers=api_auth_headers,
    )

    assert response.status_code == 404


def test_cash_sale_keeps_consistent_credit_fields(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    sale = _create_cash_sale(client, api_auth_headers, product["id"])

    assert sale["sale_type"] == "cash"
    assert sale["paid_amount"] == sale["total_amount"]
    assert sale["balance_amount"] == "0.00"
    assert sale["credit_status"] == "none"
    assert sale["due_date"] is None


def test_void_cash_sale_keeps_credit_status_none(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])

    response = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Anulacion de contado"},
    )

    assert response.status_code == 200
    assert response.json()["credit_status"] == "none"


def test_credit_sale_does_not_change_cash_or_product(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    customer = _create_credit_customer(client, api_auth_headers)
    product = _create_product(client, api_auth_headers, default_price="1.25")
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    with testing_session_local() as session:
        assert session.query(CashSession).count() == 0
        stored_product = session.get(Product, product["id"])

    assert stored_product is not None
    assert stored_product.default_price == Decimal("1.25")


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        (
            "POST",
            "/api/v1/sales/credit",
            {
                "sale_date": "2026-07-18",
                "customer_id": 1,
                "items": [{"product_id": 1, "quantity": "1"}],
            },
        ),
        ("GET", "/api/v1/sales?sale_type=credit", None),
        ("GET", "/api/v1/sales/credit/customer/1/balance", None),
        ("GET", "/api/v1/sales/1", None),
        ("POST", "/api/v1/sales/1/void", {"reason": "Motivo"}),
    ],
)
def test_credit_sale_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_credit_sales_migration_adds_credit_columns(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0009_add_credit_fields_to_sales.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0009_credit_sales",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    added_columns: list[tuple[str, object]] = []
    executed_statements: list[str] = []

    monkeypatch.setattr(
        migration.op,
        "add_column",
        lambda table_name, column: added_columns.append((table_name, column)),
    )
    monkeypatch.setattr(
        migration.op,
        "execute",
        lambda statement: executed_statements.append(statement),
    )
    monkeypatch.setattr(migration.op, "drop_constraint", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        migration.op,
        "create_check_constraint",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)

    migration.upgrade()

    assert migration.revision == "0009_credit_sales"
    assert migration.down_revision == "0008_cash_sales"
    assert len(migration.revision) <= 32
    assert [column.name for _, column in added_columns] == [
        "paid_amount",
        "balance_amount",
        "credit_status",
        "due_date",
    ]
    assert all(table_name == "sales" for table_name, _ in added_columns)
    assert "paid_amount = total_amount" in executed_statements[0]
    assert "credit_status = 'none'" in executed_statements[0]


def _create_credit_customer(
    client,
    headers: dict[str, str],
    *,
    name: str = "Tienda Don Luis",
    credit_allowed: bool = True,
    credit_limit: str = "0.00",
):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": name,
            "credit_allowed": credit_allowed,
            "credit_limit": credit_limit,
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_product(client, headers: dict[str, str], **overrides):
    payload = {
        "sku": "BIDON-20L",
        "name": "Bidon 20L",
        "category": "water",
        "unit": "container",
        "presentation": "20L",
        "default_price": "1.00",
        **overrides,
    }
    response = client.post("/api/v1/products", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()


def _credit_sale_response(
    client,
    headers: dict[str, str],
    customer_id: int,
    product_id: int,
    *,
    quantity: str = "1",
    unit_price: str | None = None,
):
    item: dict[str, object] = {"product_id": product_id, "quantity": quantity}
    if unit_price is not None:
        item["unit_price"] = unit_price
    return client.post(
        "/api/v1/sales/credit",
        headers=headers,
        json={
            "sale_date": "2026-07-18",
            "customer_id": customer_id,
            "items": [item],
        },
    )


def _create_credit_sale(
    client,
    headers: dict[str, str],
    customer_id: int,
    product_id: int | None = None,
    **overrides,
):
    items = overrides.pop("items", None)
    if items is None:
        assert product_id is not None
        item: dict[str, object] = {
            "product_id": product_id,
            "quantity": overrides.pop("quantity", "1"),
        }
        items = [item]
    payload = {
        "sale_date": "2026-07-18",
        "customer_id": customer_id,
        "items": items,
        **overrides,
    }
    response = client.post("/api/v1/sales/credit", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_cash_sale(
    client,
    headers: dict[str, str],
    product_id: int,
    **overrides,
):
    payload = {
        "sale_date": "2026-07-18",
        "items": [{"product_id": product_id, "quantity": "1"}],
        **overrides,
    }
    response = client.post("/api/v1/sales/cash", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()
