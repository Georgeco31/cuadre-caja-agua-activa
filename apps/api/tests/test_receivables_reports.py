from datetime import date, timedelta

import pytest

from app.models.credit_payment import CreditPayment
from app.models.sale import Sale


def test_receivables_summary_without_data_returns_zeroes(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/receivables/summary",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_customers_with_balance": 0,
        "total_credit_sales": "0.00",
        "total_paid": "0.00",
        "total_balance": "0.00",
    }


def test_receivables_summary_calculates_credit_totals(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    first_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="2",
    )
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="1",
    )
    _create_payment(
        client,
        api_auth_headers,
        first_sale["id"],
        amount="5.00",
    )

    summary = _get_summary(client, api_auth_headers)

    assert summary == {
        "total_customers_with_balance": 1,
        "total_credit_sales": "30.00",
        "total_paid": "5.00",
        "total_balance": "25.00",
    }


def test_receivables_summary_excludes_cash_sales(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _, product = _setup_catalog(client, api_auth_headers)
    _create_cash_sale(client, api_auth_headers, product["id"])

    summary = _get_summary(client, api_auth_headers)

    assert summary["total_credit_sales"] == "0.00"
    assert summary["total_balance"] == "0.00"


def test_receivables_summary_excludes_voided_sales(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    _void_sale(client, api_auth_headers, sale["id"])

    summary = _get_summary(client, api_auth_headers)

    assert summary["total_credit_sales"] == "0.00"
    assert summary["total_balance"] == "0.00"


def test_receivables_summary_ignores_voided_payment(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    payment = _create_payment(client, api_auth_headers, sale["id"])
    _void_payment(client, api_auth_headers, payment["id"])

    summary = _get_summary(client, api_auth_headers)

    assert summary["total_credit_sales"] == "10.00"
    assert summary["total_paid"] == "0.00"
    assert summary["total_balance"] == "10.00"


def test_receivable_customers_lists_credit_totals(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        quantity="2",
    )
    _create_payment(client, api_auth_headers, sale["id"], amount="5.00")

    response = client.get(
        "/api/v1/receivables/customers",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "customer_id": customer["id"],
            "customer_name": "Tienda Don Luis",
            "primary_phone": "0991111111",
            "sector": "Centro",
            "is_active": True,
            "total_credit_sales": "20.00",
            "total_paid": "5.00",
            "total_balance": "15.00",
            "pending_sales_count": 1,
        }
    ]


def test_only_with_balance_excludes_fully_paid_customer(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    owing_customer = _create_customer(client, api_auth_headers)
    paid_customer = _create_customer(
        client,
        api_auth_headers,
        name="Cliente Pagado",
        phone="0992222222",
    )
    _create_credit_sale(
        client,
        api_auth_headers,
        owing_customer["id"],
        product["id"],
    )
    paid_sale = _create_credit_sale(
        client,
        api_auth_headers,
        paid_customer["id"],
        product["id"],
    )
    _create_payment(
        client,
        api_auth_headers,
        paid_sale["id"],
        amount="10.00",
    )

    with_balance = client.get(
        "/api/v1/receivables/customers?only_with_balance=true",
        headers=api_auth_headers,
    ).json()
    all_movement = client.get(
        "/api/v1/receivables/customers?only_with_balance=false",
        headers=api_auth_headers,
    ).json()

    assert [item["customer_id"] for item in with_balance] == [
        owing_customer["id"]
    ]
    assert {item["customer_id"] for item in all_movement} == {
        owing_customer["id"],
        paid_customer["id"],
    }


@pytest.mark.parametrize("search", ["don luis", "0991111111"])
def test_receivable_customers_searches_name_or_phone(
    api_client,
    api_auth_headers,
    search: str,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )

    items = client.get(
        f"/api/v1/receivables/customers?search={search}",
        headers=api_auth_headers,
    ).json()

    assert [item["customer_id"] for item in items] == [customer["id"]]


def test_receivable_customers_filters_sale_date(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        sale_date="2026-06-30",
    )

    excluded = client.get(
        "/api/v1/receivables/customers?date_from=2026-07-01",
        headers=api_auth_headers,
    ).json()
    included = client.get(
        "/api/v1/receivables/customers?date_to=2026-06-30",
        headers=api_auth_headers,
    ).json()

    assert excluded == []
    assert len(included) == 1


def test_receivable_customers_filters_customer_activity(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    client.patch(
        f"/api/v1/customers/{customer['id']}/deactivate",
        headers=api_auth_headers,
    )

    inactive = client.get(
        "/api/v1/receivables/customers?is_active=false",
        headers=api_auth_headers,
    ).json()
    active = client.get(
        "/api/v1/receivables/customers?is_active=true",
        headers=api_auth_headers,
    ).json()

    assert [item["customer_id"] for item in inactive] == [customer["id"]]
    assert active == []


def test_customer_statement_lists_sales_and_payments(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        due_date="2026-07-31",
    )
    payment = _create_payment(
        client,
        api_auth_headers,
        sale["id"],
        amount="4.00",
        notes="Abono recibido",
    )

    statement = _get_statement(client, api_auth_headers, customer["id"])

    assert statement["customer_name"] == "Tienda Don Luis"
    assert statement["total_credit_sales"] == "10.00"
    assert statement["total_paid"] == "4.00"
    assert statement["total_balance"] == "6.00"
    assert statement["credit_sales"][0] == {
        "sale_id": sale["id"],
        "sale_number": sale["sale_number"],
        "sale_date": "2026-07-18",
        "due_date": "2026-07-31",
        "total_amount": "10.00",
        "paid_amount": "4.00",
        "balance_amount": "6.00",
        "credit_status": "pending",
        "status": "active",
    }
    assert statement["payments"][0]["payment_id"] == payment["id"]
    assert statement["payments"][0]["amount"] == "4.00"
    assert statement["payments"][0]["status"] == "active"


def test_customer_statement_include_paid_controls_sales_list(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    pending_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    paid_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        sale_date="2026-07-19",
    )
    _create_payment(
        client,
        api_auth_headers,
        paid_sale["id"],
        amount="10.00",
    )

    pending_only = _get_statement(
        client,
        api_auth_headers,
        customer["id"],
    )
    with_paid = _get_statement(
        client,
        api_auth_headers,
        customer["id"],
        include_paid=True,
    )

    assert [item["sale_id"] for item in pending_only["credit_sales"]] == [
        pending_sale["id"]
    ]
    assert {item["sale_id"] for item in with_paid["credit_sales"]} == {
        pending_sale["id"],
        paid_sale["id"],
    }
    assert with_paid["total_credit_sales"] == "20.00"
    assert with_paid["total_paid"] == "10.00"
    assert with_paid["total_balance"] == "10.00"


def test_customer_statement_shows_voided_payment_without_counting_it(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    payment = _create_payment(client, api_auth_headers, sale["id"])
    _void_payment(client, api_auth_headers, payment["id"])

    statement = _get_statement(client, api_auth_headers, customer["id"])

    assert statement["total_paid"] == "0.00"
    assert statement["total_balance"] == "10.00"
    assert statement["payments"][0]["status"] == "voided"
    assert statement["payments"][0]["void_reason"] == "Error de registro"


def test_customer_statement_filters_sales_by_date(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        sale_date="2026-06-30",
    )
    included_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        sale_date="2026-07-18",
    )
    _create_payment(client, api_auth_headers, included_sale["id"])

    statement = _get_statement(
        client,
        api_auth_headers,
        customer["id"],
        date_from="2026-07-01",
    )

    assert statement["total_credit_sales"] == "10.00"
    assert [item["sale_id"] for item in statement["credit_sales"]] == [
        included_sale["id"]
    ]
    assert [item["sale_id"] for item in statement["payments"]] == [
        included_sale["id"]
    ]


def test_customer_statement_missing_customer_returns_404(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/receivables/customers/999/statement",
        headers=api_auth_headers,
    )

    assert response.status_code == 404


def test_overdue_lists_only_past_due_sales_with_balance(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    past_due = (date.today() - timedelta(days=1)).isoformat()
    future_due = (date.today() + timedelta(days=1)).isoformat()
    overdue_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        due_date=past_due,
    )
    _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        due_date=future_due,
    )
    paid_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        due_date=past_due,
    )
    _create_payment(
        client,
        api_auth_headers,
        paid_sale["id"],
        amount="10.00",
    )
    voided_sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
        due_date=past_due,
    )
    _void_sale(client, api_auth_headers, voided_sale["id"])

    items = client.get(
        "/api/v1/receivables/overdue",
        headers=api_auth_headers,
    ).json()

    assert [item["sale_id"] for item in items] == [overdue_sale["id"]]


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/receivables/summary",
        "/api/v1/receivables/customers",
        "/api/v1/receivables/customers/1/statement",
        "/api/v1/receivables/overdue",
    ],
)
def test_receivables_endpoints_require_authentication(api_client, path: str) -> None:
    client, _ = api_client

    response = client.get(path)

    assert response.status_code == 401


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/receivables/summary?date_from=2026-07-31&date_to=2026-07-01",
        "/api/v1/receivables/customers?date_from=2026-07-31&date_to=2026-07-01",
        "/api/v1/receivables/customers/1/statement?date_from=2026-07-31&date_to=2026-07-01",
    ],
)
def test_receivables_reject_invalid_date_range(
    api_client,
    api_auth_headers,
    path: str,
) -> None:
    client, _ = api_client

    response = client.get(path, headers=api_auth_headers)

    assert response.status_code == 400


def test_receivables_queries_do_not_modify_sales_or_payments(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    customer, product = _setup_catalog(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    _create_payment(client, api_auth_headers, sale["id"])

    with testing_session_local() as session:
        sales_before = session.query(Sale).count()
        payments_before = session.query(CreditPayment).count()

    _get_summary(client, api_auth_headers)
    client.get(
        "/api/v1/receivables/customers",
        headers=api_auth_headers,
    )
    _get_statement(client, api_auth_headers, customer["id"])
    client.get("/api/v1/receivables/overdue", headers=api_auth_headers)

    with testing_session_local() as session:
        assert session.query(Sale).count() == sales_before
        assert session.query(CreditPayment).count() == payments_before


def _setup_catalog(client, headers: dict[str, str]):
    return _create_customer(client, headers), _create_product(client, headers)


def _create_customer(
    client,
    headers: dict[str, str],
    *,
    name: str = "Tienda Don Luis",
    phone: str = "0991111111",
):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": name,
            "primary_phone": phone,
            "sector": "Centro",
            "credit_allowed": True,
            "credit_limit": "0.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_product(client, headers: dict[str, str]):
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": "BIDON-20L",
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
    sale_date: str = "2026-07-18",
    due_date: str | None = None,
):
    response = client.post(
        "/api/v1/sales/credit",
        headers=headers,
        json={
            "sale_date": sale_date,
            "customer_id": customer_id,
            "due_date": due_date,
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


def _create_payment(
    client,
    headers: dict[str, str],
    sale_id: int,
    *,
    amount: str = "5.00",
    notes: str = "Abono recibido",
):
    response = client.post(
        f"/api/v1/sales/{sale_id}/payments",
        headers=headers,
        json={
            "payment_date": "2026-07-20",
            "amount": amount,
            "payment_method": "cash",
            "notes": notes,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _void_payment(client, headers: dict[str, str], payment_id: int) -> None:
    response = client.post(
        f"/api/v1/credit-payments/{payment_id}/void",
        headers=headers,
        json={"reason": "Error de registro"},
    )
    assert response.status_code == 200, response.text


def _void_sale(client, headers: dict[str, str], sale_id: int) -> None:
    response = client.post(
        f"/api/v1/sales/{sale_id}/void",
        headers=headers,
        json={"reason": "Venta anulada"},
    )
    assert response.status_code == 200, response.text


def _get_summary(client, headers: dict[str, str]):
    response = client.get("/api/v1/receivables/summary", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def _get_statement(
    client,
    headers: dict[str, str],
    customer_id: int,
    *,
    include_paid: bool = False,
    date_from: str | None = None,
):
    query = []
    if include_paid:
        query.append("include_paid=true")
    if date_from:
        query.append(f"date_from={date_from}")
    suffix = f"?{'&'.join(query)}" if query else ""
    response = client.get(
        f"/api/v1/receivables/customers/{customer_id}/statement{suffix}",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()
