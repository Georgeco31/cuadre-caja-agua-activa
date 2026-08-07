from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.simple_route import (
    SimpleRouteCollection,
    SimpleRouteExpense,
    SimpleRouteSale,
    SimpleRouteSheet,
)
from app.models.user import User


PERIOD_PARAMS = {
    "start_date": "2026-08-01",
    "end_date": "2026-08-02",
}


def test_admin_dashboard_without_routes_returns_route_zeroes(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/reports/admin-dashboard-analytics",
        headers=api_auth_headers,
        params=PERIOD_PARAMS,
    )

    assert response.status_code == 200
    body = response.json()
    money_fields = (
        "simple_route_sales_amount",
        "simple_route_cash_sales_amount",
        "simple_route_credit_sales_amount",
        "simple_route_partial_sales_amount",
        "simple_route_paid_amount",
        "simple_route_pending_amount",
        "simple_route_collections_amount",
        "simple_route_expenses_amount",
        "simple_route_expected_cash_amount",
        "simple_route_cash_delivered_amount",
        "simple_route_cash_difference_amount",
        "total_sales_with_routes_amount",
    )
    assert all(body[field] == "0.00" for field in money_fields)
    assert body["simple_route_best_day"] is None
    assert body["simple_route_daily_sales"] == []
    assert body["simple_route_top_routes"] == []
    assert body["simple_route_top_sellers"] == []
    assert body["simple_route_sheets_count"] == 0
    assert body["simple_route_sheets_with_difference"] == 0


def test_admin_dashboard_calculates_routes_without_mixing_official_domains(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    _seed_official_sales(session_factory)
    _seed_route_scenario(client, api_auth_headers)

    response = client.get(
        "/api/v1/reports/admin-dashboard-analytics",
        headers=api_auth_headers,
        params=PERIOD_PARAMS,
    )

    assert response.status_code == 200
    body = response.json()

    # Dominio oficial: las ventas y cobros de ruta no alteran estos importes.
    assert body["official_sales_amount"] == "180.00"
    assert body["official_cash_sales_amount"] == "100.00"
    assert body["official_credit_sales_amount"] == "80.00"
    assert body["official_credit_collections_amount"] == "20.00"
    assert body["official_credit_pending_amount"] == "60.00"
    assert body["total_sales_amount"] == "180.00"
    assert body["cash_sales_amount"] == "100.00"
    assert body["credit_sales_amount"] == "80.00"
    assert body["collections_amount"] == "20.00"
    assert body["pending_credit_amount"] == "60.00"

    # Dominio Rutas Simples: contado, fiado, parcial y abonos siguen separados.
    assert body["simple_route_sales_amount"] == "200.00"
    assert body["simple_route_cash_sales_amount"] == "130.00"
    assert body["simple_route_credit_sales_amount"] == "40.00"
    assert body["simple_route_partial_sales_amount"] == "30.00"
    assert body["simple_route_paid_amount"] == "140.00"
    assert body["simple_route_pending_amount"] == "55.00"
    assert body["simple_route_collections_amount"] == "5.00"
    assert body["simple_route_expenses_amount"] == "7.00"
    assert body["simple_route_expected_cash_amount"] == "138.00"
    assert body["simple_route_cash_delivered_amount"] == "140.00"
    assert body["simple_route_cash_difference_amount"] == "2.00"
    assert body["total_sales_with_routes_amount"] == "380.00"
    assert body["simple_route_sheets_count"] == 2
    # Ambas hojas carecen de salida física cargada, por lo que el cuadre
    # existente también detecta diferencia de producto aunque solo Norte tenga
    # diferencia de efectivo.
    assert body["simple_route_sheets_with_difference"] == 2

    assert body["simple_route_best_day"] == {
        "date": "2026-08-01",
        "amount": "120.00",
    }
    assert body["simple_route_daily_sales"] == [
        {"date": "2026-08-01", "amount": "120.00"},
        {"date": "2026-08-02", "amount": "80.00"},
    ]
    assert body["simple_route_top_routes"][0] == {
        "label": "Norte",
        "amount": "120.00",
        "count": 1,
    }
    assert body["simple_route_top_sellers"][0] == {
        "label": "George",
        "amount": "120.00",
        "count": 1,
    }


def test_admin_dashboard_route_filters_exclude_cancelled_and_outside_period(
    api_client,
    api_auth_headers,
) -> None:
    client, session_factory = api_client
    _seed_official_sales(session_factory)
    _seed_route_scenario(client, api_auth_headers)

    response = client.get(
        "/api/v1/reports/admin-dashboard-analytics",
        headers=api_auth_headers,
        params={"start_date": "2026-08-02", "end_date": "2026-08-02"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["official_sales_amount"] == "0.00"
    assert body["simple_route_sales_amount"] == "80.00"
    assert body["total_sales_with_routes_amount"] == "80.00"
    assert body["simple_route_pending_amount"] == "0.00"
    assert body["simple_route_sheets_count"] == 1
    assert body["simple_route_daily_sales"] == [
        {"date": "2026-08-02", "amount": "80.00"}
    ]


def test_admin_dashboard_route_metrics_block_operator_and_are_read_only(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, session_factory = api_client
    _seed_official_sales(session_factory)
    _seed_route_scenario(client, api_auth_headers)
    before = _business_counts(session_factory)

    admin_response = client.get(
        "/api/v1/reports/admin-dashboard-analytics",
        headers=api_auth_headers,
        params=PERIOD_PARAMS,
    )
    operator_response = client.get(
        "/api/v1/reports/admin-dashboard-analytics",
        headers=api_operator_auth_headers,
        params=PERIOD_PARAMS,
    )

    assert admin_response.status_code == 200
    assert operator_response.status_code == 403
    assert _business_counts(session_factory) == before


def _seed_official_sales(session_factory) -> None:
    with session_factory() as session:
        user = session.scalar(select(User).where(User.username == "admin"))
        assert user is not None
        customer = Customer(
            name="Cliente formal 63B",
            credit_allowed=True,
            credit_limit=Decimal("500.00"),
        )
        session.add(customer)
        session.flush()
        cash_sale = Sale(
            sale_number="63B-OFFICIAL-CASH",
            sale_date=date(2026, 8, 1),
            customer_id=customer.id,
            customer_name_snapshot=customer.name,
            sale_type="cash",
            payment_method="cash",
            status="active",
            total_amount=Decimal("100.00"),
            paid_amount=Decimal("100.00"),
            balance_amount=Decimal("0.00"),
            credit_status="none",
            created_by=user.id,
        )
        credit_sale = Sale(
            sale_number="63B-OFFICIAL-CREDIT",
            sale_date=date(2026, 8, 1),
            customer_id=customer.id,
            customer_name_snapshot=customer.name,
            sale_type="credit",
            payment_method="cash",
            status="active",
            total_amount=Decimal("80.00"),
            paid_amount=Decimal("20.00"),
            balance_amount=Decimal("60.00"),
            credit_status="pending",
            created_by=user.id,
        )
        session.add_all([cash_sale, credit_sale])
        session.flush()
        session.add(
            CreditPayment(
                sale_id=credit_sale.id,
                customer_id=customer.id,
                payment_date=date(2026, 8, 1),
                amount=Decimal("20.00"),
                payment_method="cash",
                status="active",
                created_by=user.id,
            )
        )
        session.commit()


def _seed_route_scenario(client, headers) -> None:
    north_id = _create_sheet(client, headers, 1, "George", "Norte")
    _add_sale(client, headers, north_id, "cash", "50.00")
    credit_sale_id = _add_sale(
        client,
        headers,
        north_id,
        "credit",
        "40.00",
    )
    _add_sale(client, headers, north_id, "partial", "30.00", paid="10.00")
    collection = client.post(
        f"/api/v1/simple-routes/{north_id}/collections",
        headers=headers,
        json={
            "simple_route_sale_id": credit_sale_id,
            "customer_name": "Cliente ruta Norte",
            "amount": "5.00",
        },
    )
    assert collection.status_code == 201, collection.json()
    expense = client.post(
        f"/api/v1/simple-routes/{north_id}/expenses",
        headers=headers,
        json={
            "description": "Combustible ruta Norte",
            "category": "fuel",
            "amount": "7.00",
        },
    )
    assert expense.status_code == 201, expense.json()
    _settle_sheet(client, headers, north_id, "60.00")

    south_id = _create_sheet(client, headers, 2, "Ana", "Sur")
    _add_sale(client, headers, south_id, "cash", "80.00")
    _settle_sheet(client, headers, south_id, "80.00")

    cancelled_id = _create_sheet(client, headers, 1, "Cancelado", "Oeste")
    cancelled_sale_id = _add_sale(
        client,
        headers,
        cancelled_id,
        "credit",
        "999.00",
    )
    cancelled_collection = client.post(
        f"/api/v1/simple-routes/{cancelled_id}/collections",
        headers=headers,
        json={
            "simple_route_sale_id": cancelled_sale_id,
            "amount": "9.00",
        },
    )
    assert cancelled_collection.status_code == 201, cancelled_collection.json()
    cancelled_expense = client.post(
        f"/api/v1/simple-routes/{cancelled_id}/expenses",
        headers=headers,
        json={
            "description": "Gasto cancelado",
            "category": "other",
            "amount": "9.00",
        },
    )
    assert cancelled_expense.status_code == 201, cancelled_expense.json()
    cancelled = client.post(
        f"/api/v1/simple-routes/{cancelled_id}/cancel",
        headers=headers,
        json={"reason": "No se realizó la ruta"},
    )
    assert cancelled.status_code == 200, cancelled.json()

    outside_id = _create_sheet(client, headers, 3, "Fuera", "Este")
    _add_sale(client, headers, outside_id, "cash", "500.00")


def _create_sheet(
    client,
    headers,
    day: int,
    seller: str,
    route_label: str,
) -> int:
    response = client.post(
        "/api/v1/simple-routes",
        headers=headers,
        json={
            "route_date": f"2026-08-{day:02d}",
            "seller_name": seller,
            "route_label": route_label,
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()["id"]


def _add_sale(
    client,
    headers,
    sheet_id: int,
    sale_type: str,
    total: str,
    *,
    paid: str | None = None,
) -> int:
    payload: dict[str, object] = {
        "customer_name": f"Cliente ruta {sheet_id}",
        "sale_type": sale_type,
        "items": [
            {
                "product_name": "Producto ruta 63B",
                "item_category": "other",
                "quantity": "1",
                "unit_price": total,
            }
        ],
    }
    if paid is not None:
        payload["paid_amount"] = paid
    response = client.post(
        f"/api/v1/simple-routes/{sheet_id}/sales",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201, response.json()
    return response.json()["id"]


def _settle_sheet(client, headers, sheet_id: int, cash_delivered: str) -> None:
    response = client.post(
        f"/api/v1/simple-routes/{sheet_id}/settle",
        headers=headers,
        json={"cash_delivered": cash_delivered},
    )
    assert response.status_code == 200, response.json()


def _business_counts(session_factory) -> dict[str, int]:
    models = (
        Customer,
        Sale,
        CreditPayment,
        SimpleRouteSheet,
        SimpleRouteSale,
        SimpleRouteCollection,
        SimpleRouteExpense,
    )
    with session_factory() as session:
        return {
            model.__tablename__: int(
                session.scalar(select(func.count()).select_from(model)) or 0
            )
            for model in models
        }
