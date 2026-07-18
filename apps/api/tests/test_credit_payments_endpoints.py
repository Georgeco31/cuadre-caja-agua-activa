import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.product import Product
from app.models.sale import Sale


def test_create_partial_payment_updates_sale(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    customer, _, sale = _setup_credit_sale(client, api_auth_headers)

    payment = _create_payment(client, api_auth_headers, sale["id"], amount="5.00")

    assert payment["sale_id"] == sale["id"]
    assert payment["sale_number"] == sale["sale_number"]
    assert payment["customer_id"] == customer["id"]
    assert payment["customer_name"] == customer["name"]
    assert payment["amount"] == "5.00"
    assert payment["status"] == "active"
    assert payment["sale_paid_amount"] == "5.00"
    assert payment["sale_balance_amount"] == "15.00"
    assert payment["sale_credit_status"] == "pending"

    with testing_session_local() as session:
        stored_sale = session.get(Sale, sale["id"])
        stored_payment = session.get(CreditPayment, payment["id"])
        assert stored_sale is not None
        assert stored_payment is not None
        assert stored_sale.paid_amount == Decimal("5.00")
        assert stored_sale.balance_amount == Decimal("15.00")
        assert stored_payment.customer_id == stored_sale.customer_id


def test_create_full_payment_marks_sale_paid(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)

    payment = _create_payment(client, api_auth_headers, sale["id"], amount="20.00")

    assert payment["sale_paid_amount"] == "20.00"
    assert payment["sale_balance_amount"] == "0.00"
    assert payment["sale_credit_status"] == "paid"


@pytest.mark.parametrize("amount", ["0", "-1"])
def test_payment_rejects_nonpositive_amount(
    api_client,
    api_auth_headers,
    amount: str,
) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)

    response = _payment_response(
        client,
        api_auth_headers,
        sale["id"],
        amount=amount,
    )

    assert response.status_code == 422


def test_payment_rejects_more_than_balance(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)

    response = _payment_response(
        client,
        api_auth_headers,
        sale["id"],
        amount="20.01",
    )

    assert response.status_code == 400
    assert "mayor al saldo pendiente" in response.json()["detail"]


def test_payment_rejects_cash_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])

    response = _payment_response(client, api_auth_headers, sale["id"])

    assert response.status_code == 400
    assert "ventas a credito" in response.json()["detail"]


def test_payment_rejects_voided_credit_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Venta anulada"},
    )

    response = _payment_response(client, api_auth_headers, sale["id"])

    assert response.status_code == 400
    assert "venta anulada" in response.json()["detail"]


def test_payment_rejects_missing_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = _payment_response(client, api_auth_headers, 999)

    assert response.status_code == 404


def test_payment_rejects_already_paid_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    _create_payment(client, api_auth_headers, sale["id"], amount="20.00")

    response = _payment_response(client, api_auth_headers, sale["id"])

    assert response.status_code == 409
    assert "ya esta pagada" in response.json()["detail"]


def test_payment_rejects_more_than_two_decimals(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)

    response = _payment_response(
        client,
        api_auth_headers,
        sale["id"],
        amount="1.001",
    )

    assert response.status_code == 422


@pytest.mark.parametrize("method", ["cash", "transfer", "card", "other"])
def test_payment_accepts_supported_methods(
    api_client,
    api_auth_headers,
    method: str,
) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)

    payment = _create_payment(
        client,
        api_auth_headers,
        sale["id"],
        payment_method=method,
    )

    assert payment["payment_method"] == method


def test_list_payments_for_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    first = _create_payment(client, api_auth_headers, sale["id"], amount="3.00")
    second = _create_payment(client, api_auth_headers, sale["id"], amount="4.00")

    response = client.get(
        f"/api/v1/sales/{sale['id']}/payments",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {first["id"], second["id"]}


def test_list_payments_for_missing_sale_returns_404(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/sales/999/payments",
        headers=api_auth_headers,
    )

    assert response.status_code == 404


def test_list_payments_filters_by_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer, product, first_sale = _setup_credit_sale(client, api_auth_headers)
    second_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    _create_payment(client, api_auth_headers, first_sale["id"])
    expected = _create_payment(client, api_auth_headers, second_sale["id"])

    items = client.get(
        f"/api/v1/credit-payments?sale_id={second_sale['id']}",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in items] == [expected["id"]]


def test_list_payments_filters_by_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, first_sale = _setup_credit_sale(client, api_auth_headers)
    second_customer = _create_customer(client, api_auth_headers, name="Cliente Dos")
    second_product = _create_product(
        client,
        api_auth_headers,
        sku="BOT-500",
    )
    second_sale = _create_credit_sale(
        client,
        api_auth_headers,
        second_customer["id"],
        second_product["id"],
    )
    _create_payment(client, api_auth_headers, first_sale["id"])
    expected = _create_payment(client, api_auth_headers, second_sale["id"])

    items = client.get(
        f"/api/v1/credit-payments?customer_id={second_customer['id']}",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in items] == [expected["id"]]


def test_list_payments_filters_by_date(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    _create_payment(
        client,
        api_auth_headers,
        sale["id"],
        payment_date="2026-07-01",
    )
    expected = _create_payment(
        client,
        api_auth_headers,
        sale["id"],
        payment_date="2026-07-20",
    )

    items = client.get(
        "/api/v1/credit-payments?date_from=2026-07-10&date_to=2026-07-31",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in items] == [expected["id"]]


def test_list_payments_rejects_invalid_date_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/credit-payments?date_from=2026-07-31&date_to=2026-07-01",
        headers=api_auth_headers,
    )

    assert response.status_code == 400


def test_list_payments_filters_by_status(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    voided = _create_payment(client, api_auth_headers, sale["id"], amount="3.00")
    active = _create_payment(client, api_auth_headers, sale["id"], amount="4.00")
    _void_payment(client, api_auth_headers, voided["id"])

    active_items = client.get(
        "/api/v1/credit-payments?status=active",
        headers=api_auth_headers,
    ).json()
    voided_items = client.get(
        "/api/v1/credit-payments?status=voided",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in active_items] == [active["id"]]
    assert [item["id"] for item in voided_items] == [voided["id"]]


def test_list_payments_filters_by_method(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    _create_payment(
        client,
        api_auth_headers,
        sale["id"],
        payment_method="cash",
    )
    expected = _create_payment(
        client,
        api_auth_headers,
        sale["id"],
        payment_method="transfer",
    )

    items = client.get(
        "/api/v1/credit-payments?payment_method=transfer",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in items] == [expected["id"]]


def test_void_partial_payment_restores_sale(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"], amount="5.00")

    voided = _void_payment(client, api_auth_headers, payment["id"])

    assert voided["status"] == "voided"
    assert voided["void_reason"] == "Error de registro"
    assert voided["voided_at"] is not None
    assert voided["sale_paid_amount"] == "0.00"
    assert voided["sale_balance_amount"] == "20.00"
    assert voided["sale_credit_status"] == "pending"


def test_void_full_payment_reopens_balance(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"], amount="20.00")

    voided = _void_payment(client, api_auth_headers, payment["id"])

    assert voided["sale_paid_amount"] == "0.00"
    assert voided["sale_balance_amount"] == "20.00"
    assert voided["sale_credit_status"] == "pending"


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_payment_requires_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"])

    response = client.post(
        f"/api/v1/credit-payments/{payment['id']}/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_void_payment_cannot_be_repeated(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"])
    _void_payment(client, api_auth_headers, payment["id"])

    response = client.post(
        f"/api/v1/credit-payments/{payment['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Segundo intento"},
    )

    assert response.status_code == 409


def test_void_payment_does_not_delete_record(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"])
    _void_payment(client, api_auth_headers, payment["id"])

    with testing_session_local() as session:
        stored_payment = session.get(CreditPayment, payment["id"])

    assert stored_payment is not None
    assert stored_payment.status == "voided"


def test_sale_with_active_payment_cannot_be_voided(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"])

    blocked = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Venta incorrecta"},
    )
    _void_payment(client, api_auth_headers, payment["id"])
    allowed = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Venta incorrecta"},
    )

    assert blocked.status_code == 409
    assert allowed.status_code == 200


def test_customer_balance_includes_active_payment(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, _, sale = _setup_credit_sale(client, api_auth_headers)
    _create_payment(client, api_auth_headers, sale["id"], amount="5.00")

    balance = _get_balance(client, api_auth_headers, customer["id"])

    assert balance["total_credit_sales"] == "20.00"
    assert balance["total_paid"] == "5.00"
    assert balance["total_balance"] == "15.00"


def test_customer_balance_includes_fully_paid_sale(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, _, sale = _setup_credit_sale(client, api_auth_headers)
    _create_payment(client, api_auth_headers, sale["id"], amount="20.00")

    balance = _get_balance(client, api_auth_headers, customer["id"])

    assert balance["total_credit_sales"] == "20.00"
    assert balance["total_paid"] == "20.00"
    assert balance["total_balance"] == "0.00"


def test_customer_balance_ignores_voided_payment(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"], amount="5.00")
    _void_payment(client, api_auth_headers, payment["id"])

    balance = _get_balance(client, api_auth_headers, customer["id"])

    assert balance["total_credit_sales"] == "20.00"
    assert balance["total_paid"] == "0.00"
    assert balance["total_balance"] == "20.00"


def test_customer_balance_ignores_voided_sale(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, _, sale = _setup_credit_sale(client, api_auth_headers)
    payment = _create_payment(client, api_auth_headers, sale["id"])
    _void_payment(client, api_auth_headers, payment["id"])
    client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Venta anulada"},
    )

    balance = _get_balance(client, api_auth_headers, customer["id"])

    assert balance["total_credit_sales"] == "0.00"
    assert balance["total_paid"] == "0.00"
    assert balance["total_balance"] == "0.00"


def test_payment_does_not_change_cash_or_product(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _, product, sale = _setup_credit_sale(client, api_auth_headers)

    with testing_session_local() as session:
        cash_sessions_before = session.query(CashSession).count()
        stored_product = session.get(Product, product["id"])
        assert stored_product is not None
        product_price_before = stored_product.default_price

    _create_payment(client, api_auth_headers, sale["id"])

    with testing_session_local() as session:
        assert session.query(CashSession).count() == cash_sessions_before
        stored_product = session.get(Product, product["id"])
        assert stored_product is not None
        assert stored_product.default_price == product_price_before


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/sales/1/payments",
            {
                "payment_date": "2026-07-18",
                "amount": "5.00",
                "payment_method": "cash",
            },
        ),
        ("GET", "/api/v1/sales/1/payments", None),
        ("GET", "/api/v1/credit-payments", None),
        (
            "POST",
            "/api/v1/credit-payments/1/void",
            {"reason": "Error"},
        ),
    ],
)
def test_credit_payment_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, str] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_credit_payments_migration_creates_table(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0010_create_credit_payments.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0010_payments",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    created_tables: list[tuple[str, tuple[object, ...]]] = []
    created_indexes: list[str] = []
    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda name, *items, **kwargs: created_tables.append((name, items)),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda name, *args, **kwargs: created_indexes.append(name),
    )

    migration.upgrade()

    assert migration.revision == "0010_payments"
    assert migration.down_revision == "0009_credit_sales"
    assert len(migration.revision) <= 32
    assert created_tables[0][0] == "credit_payments"
    column_names = {
        item.name for item in created_tables[0][1] if hasattr(item, "name")
    }
    assert {
        "id",
        "sale_id",
        "customer_id",
        "payment_date",
        "amount",
        "payment_method",
        "status",
        "notes",
        "void_reason",
        "voided_at",
        "created_by",
        "created_at",
        "updated_at",
    } <= column_names
    assert "ix_credit_payments_sale_id" in created_indexes
    assert "ix_credit_payments_customer_id" in created_indexes


def _setup_credit_sale(client, headers: dict[str, str]):
    customer = _create_customer(client, headers)
    product = _create_product(client, headers)
    sale = _create_credit_sale(
        client,
        headers,
        customer["id"],
        product["id"],
        quantity="2",
    )
    return customer, product, sale


def _create_customer(
    client,
    headers: dict[str, str],
    *,
    name: str = "Tienda Don Luis",
):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": name,
            "credit_allowed": True,
            "credit_limit": "0.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_product(
    client,
    headers: dict[str, str],
    *,
    sku: str = "BIDON-20L",
):
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": sku,
            "name": "Bidon 20L",
            "category": "water",
            "unit": "container",
            "presentation": "20L",
            "default_price": "10.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_credit_sale(
    client,
    headers: dict[str, str],
    customer_id: int,
    product_id: int,
    *,
    quantity: str = "1",
):
    response = client.post(
        "/api/v1/sales/credit",
        headers=headers,
        json={
            "sale_date": "2026-07-18",
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": quantity}],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_cash_sale(client, headers: dict[str, str], product_id: int):
    response = client.post(
        "/api/v1/sales/cash",
        headers=headers,
        json={
            "sale_date": "2026-07-18",
            "items": [{"product_id": product_id, "quantity": "1"}],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _payment_response(
    client,
    headers: dict[str, str],
    sale_id: int,
    *,
    amount: str = "5.00",
    payment_date: str = "2026-07-18",
    payment_method: str = "cash",
):
    return client.post(
        f"/api/v1/sales/{sale_id}/payments",
        headers=headers,
        json={
            "payment_date": payment_date,
            "amount": amount,
            "payment_method": payment_method,
            "notes": "Abono recibido en oficina",
        },
    )


def _create_payment(client, headers: dict[str, str], sale_id: int, **overrides):
    response = _payment_response(client, headers, sale_id, **overrides)
    assert response.status_code == 201, response.text
    return response.json()


def _void_payment(client, headers: dict[str, str], payment_id: int):
    response = client.post(
        f"/api/v1/credit-payments/{payment_id}/void",
        headers=headers,
        json={"reason": "Error de registro"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _get_balance(client, headers: dict[str, str], customer_id: int):
    response = client.get(
        f"/api/v1/sales/credit/customer/{customer_id}/balance",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()
