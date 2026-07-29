import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy.dialects import postgresql

from app.models.cash_session import CashSession
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.repositories import sales as sale_repository


def test_create_cash_sale_with_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_customer(client, api_auth_headers, "Tienda Don Luis")
    product = _create_product(client, api_auth_headers)

    body = _create_sale(
        client,
        api_auth_headers,
        customer_id=customer["id"],
        items=[{"product_id": product["id"], "quantity": "3"}],
    )

    assert body["sale_number"].startswith("SALE-20260718-")
    assert body["customer_id"] == customer["id"]
    assert body["customer_name_snapshot"] == "Tienda Don Luis"
    assert body["sale_type"] == "cash"
    assert body["status"] == "active"
    assert body["created_by"] is not None


def test_create_cash_sale_without_customer_uses_final_consumer(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    body = _create_sale(client, api_auth_headers, product_id=product["id"])

    assert body["customer_id"] is None
    assert body["customer_name_snapshot"] == "Consumidor final"


def test_create_cash_sale_with_multiple_products(api_client, api_auth_headers) -> None:
    client, _ = api_client
    first = _create_product(client, api_auth_headers, name="Bidon 20L")
    second = _create_product(
        client,
        api_auth_headers,
        name="Botella 500ml",
        sku="BOT-500",
        presentation="500ml",
        default_price="0.50",
    )

    body = _create_sale(
        client,
        api_auth_headers,
        items=[
            {"product_id": first["id"], "quantity": "2"},
            {"product_id": second["id"], "quantity": "4"},
        ],
    )

    assert [item["product_name_snapshot"] for item in body["items"]] == [
        "Bidon 20L",
        "Botella 500ml",
    ]


def test_create_cash_sale_uses_product_default_price(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers, default_price="1.35")

    body = _create_sale(client, api_auth_headers, product_id=product["id"])

    assert body["items"][0]["unit_price"] == "1.35"


def test_create_cash_sale_allows_adjusted_unit_price(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers, default_price="1.35")

    body = _create_sale(
        client,
        api_auth_headers,
        items=[
            {"product_id": product["id"], "quantity": "2", "unit_price": "1.10"}
        ],
    )

    assert body["items"][0]["unit_price"] == "1.10"


def test_create_cash_sale_calculates_subtotal_in_backend(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    body = _create_sale(
        client,
        api_auth_headers,
        items=[
            {"product_id": product["id"], "quantity": "2.5", "unit_price": "1.20"}
        ],
    )

    assert body["items"][0]["subtotal"] == "3.00"


def test_create_cash_sale_rounds_money_to_two_decimals(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    body = _create_sale(
        client,
        api_auth_headers,
        items=[
            {"product_id": product["id"], "quantity": "0.333", "unit_price": "1.00"}
        ],
    )

    assert body["items"][0]["subtotal"] == "0.33"
    assert body["total_amount"] == "0.33"


def test_create_cash_sale_calculates_total_amount(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first = _create_product(client, api_auth_headers)
    second = _create_product(client, api_auth_headers, name="Botella", sku="BOT-1")

    body = _create_sale(
        client,
        api_auth_headers,
        items=[
            {"product_id": first["id"], "quantity": "3", "unit_price": "1.00"},
            {"product_id": second["id"], "quantity": "2", "unit_price": "0.75"},
        ],
    )

    assert body["total_amount"] == "4.50"


def test_create_cash_sale_requires_items(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={"sale_date": "2026-07-18", "items": []},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("quantity", ["0", "-1"])
def test_create_cash_sale_rejects_nonpositive_quantity(
    api_client,
    api_auth_headers,
    quantity: str,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-18",
            "items": [{"product_id": product["id"], "quantity": quantity}],
        },
    )

    assert response.status_code == 422


def test_create_cash_sale_rejects_negative_unit_price(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-18",
            "items": [
                {"product_id": product["id"], "quantity": "1", "unit_price": "-0.01"}
            ],
        },
    )

    assert response.status_code == 422


def test_create_cash_sale_requires_sale_date(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={"items": [{"product_id": product["id"], "quantity": "1"}]},
    )

    assert response.status_code == 422


def test_create_cash_sale_rejects_missing_customer(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-18",
            "customer_id": 999,
            "items": [{"product_id": product["id"], "quantity": "1"}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El cliente no existe."


def test_create_cash_sale_rejects_missing_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-18",
            "items": [{"product_id": 999, "quantity": "1"}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El producto 999 no existe."


def test_create_cash_sale_rejects_inactive_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.post(
        "/api/v1/sales/cash",
        headers=api_auth_headers,
        json={
            "sale_date": "2026-07-18",
            "items": [{"product_id": product["id"], "quantity": "1"}],
        },
    )

    assert response.status_code == 400
    assert "esta inactivo" in response.json()["detail"]


def test_create_cash_sale_keeps_customer_and_product_snapshots(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer = _create_customer(client, api_auth_headers, "Cliente original")
    product = _create_product(client, api_auth_headers, name="Producto original")
    sale = _create_sale(
        client,
        api_auth_headers,
        customer_id=customer["id"],
        product_id=product["id"],
    )
    client.patch(
        f"/api/v1/customers/{customer['id']}",
        headers=api_auth_headers,
        json={"name": "Cliente actualizado"},
    )
    client.patch(
        f"/api/v1/products/{product['id']}",
        headers=api_auth_headers,
        json={"name": "Producto actualizado"},
    )

    detail = client.get(
        f"/api/v1/sales/{sale['id']}",
        headers=api_auth_headers,
    ).json()

    assert detail["customer_name_snapshot"] == "Cliente original"
    assert detail["items"][0]["product_name_snapshot"] == "Producto original"


def test_create_cash_sale_generates_unique_numbers(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    first = _create_sale(client, api_auth_headers, product_id=product["id"])
    second = _create_sale(client, api_auth_headers, product_id=product["id"])

    assert first["sale_number"] != second["sale_number"]


def test_list_cash_sales(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    first = _create_sale(client, api_auth_headers, product_id=product["id"])
    second = _create_sale(
        client,
        api_auth_headers,
        product_id=product["id"],
        sale_date="2026-07-19",
    )

    response = client.get("/api/v1/sales", headers=api_auth_headers)

    assert response.status_code == 200
    assert [sale["id"] for sale in response.json()] == [second["id"], first["id"]]


def test_list_cash_sales_filters_by_date_range(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    _create_sale(client, api_auth_headers, product_id=product["id"], sale_date="2026-07-01")
    expected = _create_sale(
        client,
        api_auth_headers,
        product_id=product["id"],
        sale_date="2026-07-15",
    )
    _create_sale(client, api_auth_headers, product_id=product["id"], sale_date="2026-08-01")

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"date_from": "2026-07-10", "date_to": "2026-07-20"},
    )

    assert [sale["id"] for sale in response.json()] == [expected["id"]]


def test_list_cash_sales_rejects_inverted_date_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"date_from": "2026-07-20", "date_to": "2026-07-10"},
    )

    assert response.status_code == 400


def test_list_cash_sales_filters_by_status(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    active = _create_sale(client, api_auth_headers, product_id=product["id"])
    voided = _create_sale(client, api_auth_headers, product_id=product["id"])
    client.post(
        f"/api/v1/sales/{voided['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Registro duplicado"},
    )

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"status": "active"},
    )

    assert [sale["id"] for sale in response.json()] == [active["id"]]


def test_list_cash_sales_filters_by_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    customer = _create_customer(client, api_auth_headers, "Cliente filtrado")
    expected = _create_sale(
        client,
        api_auth_headers,
        customer_id=customer["id"],
        product_id=product["id"],
    )
    _create_sale(client, api_auth_headers, product_id=product["id"])

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"customer_id": customer["id"]},
    )

    assert [sale["id"] for sale in response.json()] == [expected["id"]]


def test_list_cash_sales_filters_by_payment_method(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    expected = _create_sale(
        client,
        api_auth_headers,
        product_id=product["id"],
        payment_method="transfer",
    )
    _create_sale(client, api_auth_headers, product_id=product["id"])

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"payment_method": "transfer"},
    )

    assert [sale["id"] for sale in response.json()] == [expected["id"]]


@pytest.mark.parametrize("search_kind", ["customer", "number"])
def test_list_cash_sales_searches_snapshot_or_sale_number(
    api_client,
    api_auth_headers,
    search_kind: str,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    customer = _create_customer(client, api_auth_headers, "Tienda Las Palmas")
    expected = _create_sale(
        client,
        api_auth_headers,
        customer_id=customer["id"],
        product_id=product["id"],
    )
    search = "palmas" if search_kind == "customer" else expected["sale_number"]

    response = client.get(
        "/api/v1/sales",
        headers=api_auth_headers,
        params={"search": search},
    )

    assert [sale["id"] for sale in response.json()] == [expected["id"]]


def test_get_cash_sale_detail(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_sale(client, api_auth_headers, product_id=product["id"])

    response = client.get(
        f"/api/v1/sales/{sale['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == sale


def test_get_cash_sale_detail_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get("/api/v1/sales/999", headers=api_auth_headers)

    assert response.status_code == 404


def test_void_cash_sale_with_reason(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_sale(client, api_auth_headers, product_id=product["id"])

    response = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": " Error al registrar la venta "},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "voided"
    assert body["void_reason"] == "Error al registrar la venta"
    assert body["voided_at"] is not None


def test_sale_for_update_locks_only_sale_table_on_postgresql() -> None:
    class StatementCapturingSession:
        statement = None

        def scalar(self, statement):
            self.statement = statement
            return None

    session = StatementCapturingSession()

    sale_repository.get_sale_for_update(session, 1)

    assert session.statement is not None
    compiled = str(
        session.statement.compile(dialect=postgresql.dialect()),
    )
    assert "LEFT OUTER JOIN" in compiled
    assert "FOR UPDATE OF sales" in compiled


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_cash_sale_requires_nonblank_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_sale(client, api_auth_headers, product_id=product["id"])

    response = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_void_cash_sale_cannot_be_repeated(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_sale(client, api_auth_headers, product_id=product["id"])
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
    assert response.json()["detail"] == "La venta ya esta anulada."


def test_void_cash_sale_preserves_sale_and_items(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_sale(client, api_auth_headers, product_id=product["id"])
    client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Anulacion controlada"},
    )

    with testing_session_local() as session:
        stored_sale = session.get(Sale, sale["id"])
        stored_items = session.query(SaleItem).filter_by(sale_id=sale["id"]).all()

    assert stored_sale is not None
    assert stored_sale.status == "voided"
    assert len(stored_items) == 1


def test_cash_sale_does_not_change_cash_or_product_price(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers, default_price="1.25")
    _create_sale(
        client,
        api_auth_headers,
        product_id=product["id"],
        items=[
            {"product_id": product["id"], "quantity": "3", "unit_price": "1.00"}
        ],
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
            "/api/v1/sales/cash",
            {"sale_date": "2026-07-18", "items": [{"product_id": 1, "quantity": "1"}]},
        ),
        ("GET", "/api/v1/sales", None),
        ("GET", "/api/v1/sales/1", None),
        ("POST", "/api/v1/sales/1/void", {"reason": "Motivo"}),
    ],
)
def test_cash_sale_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_cash_sales_migration_creates_sales_and_sale_items(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0008_create_cash_sales.py"
    )
    spec = importlib.util.spec_from_file_location("migration_0008_cash_sales", migration_path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[tuple[str, tuple[object, ...]]] = []

    def record_create_table(table_name: str, *elements: object) -> None:
        created_tables.append((table_name, elements))

    monkeypatch.setattr(migration.op, "create_table", record_create_table)
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)

    migration.upgrade()

    assert migration.revision == "0008_cash_sales"
    assert migration.down_revision == "0007_vehicles"
    assert len(migration.revision) <= 32
    assert [table_name for table_name, _ in created_tables] == ["sales", "sale_items"]
    sales_columns = _column_names(created_tables[0][1])
    sale_item_columns = _column_names(created_tables[1][1])
    assert {"sale_number", "customer_name_snapshot", "total_amount", "void_reason"} <= sales_columns
    assert {"sale_id", "product_id", "quantity", "unit_price", "subtotal"} <= sale_item_columns


def _create_customer(client, headers: dict[str, str], name: str):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name},
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


def _create_sale(
    client,
    headers: dict[str, str],
    product_id: int | None = None,
    **overrides,
):
    items = overrides.pop("items", None)
    if items is None:
        assert product_id is not None
        items = [{"product_id": product_id, "quantity": "1"}]
    payload = {
        "sale_date": "2026-07-18",
        "payment_method": "cash",
        "items": items,
        **overrides,
    }
    response = client.post("/api/v1/sales/cash", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _column_names(elements: tuple[object, ...]) -> set[str]:
    return {
        element.name
        for element in elements
        if element.__class__.__name__ == "Column"
    }
