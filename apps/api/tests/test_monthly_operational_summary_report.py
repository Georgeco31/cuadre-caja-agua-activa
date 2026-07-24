from datetime import date

from tests.test_daily_operational_summary_report import (
    REPORT_DATE,
    _add_complete_daily_operation,
    _database_snapshot,
)

REPORT_PATH = "/api/v1/reports/monthly-operational-summary"


def test_monthly_operational_summary_requires_authentication(api_client) -> None:
    client, _ = api_client

    response = client.get(REPORT_PATH)

    assert response.status_code == 401


def test_monthly_operational_summary_without_data_returns_every_day_and_alerts(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        f"{REPORT_PATH}?year=2026&month=2",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["period"] == {
        "year": 2026,
        "month": 2,
        "date_from": "2026-02-01",
        "date_to": "2026-02-28",
        "days_in_month": 28,
    }
    assert body["cash_summary"] == {
        "cash_sessions_count": 0,
        "open_cash_sessions_count": 0,
        "closed_cash_sessions_count": 0,
        "total_coins": "0.00",
        "total_bills": "0.00",
        "total_counted": "0.00",
        "total_expenses": "0.00",
        "total_final": "0.00",
        "average_daily_counted": "0.00",
        "days_with_cash_session": 0,
        "days_without_cash_session": 28,
    }
    assert len(body["daily_rows"]) == 28
    assert body["daily_rows"][0]["date"] == "2026-02-01"
    assert body["daily_rows"][-1]["date"] == "2026-02-28"
    assert body["daily_rows"][0]["alert_codes"] == [
        "cash_session_missing",
        "no_production",
        "no_sales",
    ]
    assert body["alerts_summary"] == {
        "total_alerts": 84,
        "days_with_alerts_count": 28,
        "alerts_by_code": [
            {
                "code": "cash_session_missing",
                "count": 28,
                "message": "No existe cuadre de caja para este día.",
            },
            {
                "code": "no_production",
                "count": 28,
                "message": "No hay producción activa registrada para este día.",
            },
            {
                "code": "no_sales",
                "count": 28,
                "message": "No hay ventas activas registradas para este día.",
            },
        ],
    }
    assert body["totals"] == {
        "total_business_cash_inflow_reference": "0.00",
    }


def test_monthly_operational_summary_without_period_uses_current_month(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(REPORT_PATH, headers=api_auth_headers)

    assert response.status_code == 200
    today = date.today()
    assert response.json()["period"]["year"] == today.year
    assert response.json()["period"]["month"] == today.month


def test_monthly_operational_summary_validates_period(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    invalid_month = client.get(
        f"{REPORT_PATH}?year=2026&month=13",
        headers=api_auth_headers,
    )
    invalid_year = client.get(
        f"{REPORT_PATH}?year=0&month=1",
        headers=api_auth_headers,
    )

    assert invalid_month.status_code == 422
    assert invalid_year.status_code == 422


def test_monthly_operational_summary_aggregates_and_excludes_voided_records(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _add_complete_daily_operation(
        testing_session_local,
        coin_id=api_denominations["coin_100"].id,
        bill_id=api_denominations["bill_1000"].id,
    )

    response = client.get(
        f"{REPORT_PATH}?year={REPORT_DATE.year}&month={REPORT_DATE.month}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()

    assert body["period"] == {
        "year": 2026,
        "month": 7,
        "date_from": "2026-07-01",
        "date_to": "2026-07-31",
        "days_in_month": 31,
    }
    assert body["cash_summary"] == {
        "cash_sessions_count": 1,
        "open_cash_sessions_count": 1,
        "closed_cash_sessions_count": 0,
        "total_coins": "2.00",
        "total_bills": "30.00",
        "total_counted": "32.00",
        "total_expenses": "2.00",
        "total_final": "30.00",
        "average_daily_counted": "32.00",
        "days_with_cash_session": 1,
        "days_without_cash_session": 30,
    }

    production = body["production_summary"]
    assert production["production_batches_count"] == 2
    assert production["active_production_batches_count"] == 1
    assert production["voided_production_batches_count"] == 1
    assert production["total_quantity_produced"] == "15.000"
    assert production["total_quantity_waste"] == "1.500"
    assert production["total_quantity_net"] == "13.500"
    assert [
        (item["product_name_snapshot"], item["quantity_net"])
        for item in production["products"]
    ] == [("Botella", "4.500"), ("Galón", "9.000")]

    sales = body["sales_summary"]
    assert sales["cash_sales_total"] == "60.00"
    assert sales["credit_sales_total"] == "40.00"
    assert sales["total_sales_amount"] == "100.00"
    assert sales["cash_sales_count"] == 1
    assert sales["credit_sales_count"] == 1
    assert sales["voided_sales_count"] == 1
    assert [
        (item["product_name_snapshot"], item["quantity"], item["amount"])
        for item in sales["products_sold"]
    ] == [
        ("Botella", "2.000", "20.00"),
        ("Galón", "4.000", "80.00"),
    ]

    assert body["receivables_summary"] == {
        "payments_total": "15.00",
        "payments_count": 1,
        "voided_payments_count": 1,
        "credit_sales_created_total": "40.00",
        "pending_credit_total": "25.00",
        "customers_with_credit_sales_count": 1,
    }
    assert body["route_operations_summary"] == {
        "route_loads_count": 4,
        "active_route_loads_count": 3,
        "voided_route_loads_count": 1,
        "route_returns_count": 2,
        "active_route_returns_count": 1,
        "voided_route_returns_count": 1,
        "total_quantity_loaded": "21.000",
        "total_quantity_returned": "5.000",
    }
    assert body["route_financial_summary"] == {
        "route_closures_count": 3,
        "active_route_closures_count": 2,
        "voided_route_closures_count": 1,
        "expected_cash_total": "180.00",
        "delivered_cash_total": "175.00",
        "difference_total": "-5.00",
        "closures_with_shortage_count": 1,
        "closures_with_surplus_count": 0,
        "closures_balanced_count": 1,
    }
    assert body["route_cash_receipts_summary"] == {
        "receipts_count": 2,
        "active_receipts_count": 1,
        "voided_receipts_count": 1,
        "delivered_cash_total": "100.00",
        "received_amount_total": "101.00",
        "difference_total": "1.00",
    }

    report_day = next(
        row
        for row in body["daily_rows"]
        if row["date"] == REPORT_DATE.isoformat()
    )
    assert report_day == {
        "date": "2026-07-23",
        "cash_session_exists": True,
        "cash_total_counted": "32.00",
        "cash_total_expenses": "2.00",
        "cash_total_final": "30.00",
        "production_quantity_net": "13.500",
        "cash_sales_total": "60.00",
        "credit_sales_total": "40.00",
        "payments_total": "15.00",
        "route_delivered_cash_total": "175.00",
        "route_cash_registered_total": "101.00",
        "alerts_count": 5,
        "alert_codes": [
            "cash_session_open",
            "route_shortage",
            "route_closure_without_cash_receipt",
            "route_cash_receipt_difference",
            "routes_loaded_without_closure",
        ],
    }
    assert {
        item["code"]: item["count"]
        for item in body["alerts_summary"]["alerts_by_code"]
    } == {
        "cash_session_missing": 30,
        "cash_session_open": 1,
        "route_shortage": 1,
        "route_closure_without_cash_receipt": 1,
        "route_cash_receipt_difference": 1,
        "no_production": 30,
        "no_sales": 30,
        "routes_loaded_without_closure": 1,
    }
    assert body["alerts_summary"]["total_alerts"] == 95
    assert body["alerts_summary"]["days_with_alerts_count"] == 31
    assert body["totals"] == {
        "total_business_cash_inflow_reference": "176.00",
    }


def test_monthly_operational_summary_is_read_only(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _add_complete_daily_operation(
        testing_session_local,
        coin_id=api_denominations["coin_100"].id,
        bill_id=api_denominations["bill_1000"].id,
    )
    before = _database_snapshot(testing_session_local)

    response = client.get(
        f"{REPORT_PATH}?year={REPORT_DATE.year}&month={REPORT_DATE.month}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert _database_snapshot(testing_session_local) == before
