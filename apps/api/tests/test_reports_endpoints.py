from decimal import Decimal


def test_cash_summary_report_without_token_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/reports/cash-summary")

    assert response.status_code == 401


def test_cash_summary_report_without_sessions_returns_zeroes(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/reports/cash-summary",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "date_from": None,
        "date_to": None,
        "status": None,
        "total_sessions": 0,
        "open_sessions": 0,
        "closed_sessions": 0,
        "total_coins": "0.00",
        "total_bills": "0.00",
        "total_counted": "0.00",
        "total_pre_count_expenses": "0.00",
        "total_post_count_expenses": "0.00",
        "total_expenses": "0.00",
        "final_total": "0.00",
    }


def test_cash_summary_report_calculates_accumulated_totals(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_session_id = _create_cash_session(
        client,
        api_auth_headers,
        session_date="2026-07-01",
    )
    second_session_id = _create_cash_session(
        client,
        api_auth_headers,
        session_date="2026-07-02",
    )
    _set_count(
        client,
        first_session_id,
        api_denominations["coin_025"].id,
        4,
        api_auth_headers,
    )
    _set_count(
        client,
        first_session_id,
        api_denominations["bill_1000"].id,
        2,
        api_auth_headers,
    )
    _create_expense(
        client,
        first_session_id,
        Decimal("1.50"),
        api_auth_headers,
        expense_timing="before_count",
    )
    _create_expense(
        client,
        first_session_id,
        Decimal("5.00"),
        api_auth_headers,
    )
    _close_cash_session(client, first_session_id, api_auth_headers)
    _set_count(
        client,
        second_session_id,
        api_denominations["coin_100"].id,
        3,
        api_auth_headers,
    )
    _set_count(
        client,
        second_session_id,
        api_denominations["bill_2000"].id,
        1,
        api_auth_headers,
    )
    _create_expense(
        client,
        second_session_id,
        Decimal("2.50"),
        api_auth_headers,
    )

    response = client.get(
        "/api/v1/reports/cash-summary",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_sessions"] == 2
    assert body["open_sessions"] == 1
    assert body["closed_sessions"] == 1
    assert body["total_coins"] == "4.00"
    assert body["total_bills"] == "40.00"
    assert body["total_counted"] == "44.00"
    assert body["total_pre_count_expenses"] == "1.50"
    assert body["total_post_count_expenses"] == "7.50"
    assert body["total_expenses"] == "7.50"
    assert body["final_total"] == "36.50"


def test_cash_summary_report_filters_by_date_range(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_1000"].id,
        "2026-07-01",
        1,
    )
    selected_session_id = _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_1000"].id,
        "2026-07-02",
        2,
    )
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_1000"].id,
        "2026-07-03",
        3,
    )
    _create_expense(client, selected_session_id, Decimal("4.00"), api_auth_headers)

    response = client.get(
        (
            "/api/v1/reports/cash-summary"
            "?date_from=2026-07-02&date_to=2026-07-02"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["date_from"] == "2026-07-02"
    assert body["date_to"] == "2026-07-02"
    assert body["total_sessions"] == 1
    assert body["total_coins"] == "0.00"
    assert body["total_bills"] == "20.00"
    assert body["total_counted"] == "20.00"
    assert body["total_pre_count_expenses"] == "0.00"
    assert body["total_post_count_expenses"] == "4.00"
    assert body["total_expenses"] == "4.00"
    assert body["final_total"] == "16.00"


def test_cash_summary_report_filters_by_status(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    closed_session_id = _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_1000"].id,
        "2026-07-01",
        2,
    )
    _close_cash_session(client, closed_session_id, api_auth_headers)
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_1000"].id,
        "2026-07-02",
        4,
    )

    response = client.get(
        "/api/v1/reports/cash-summary?status=closed",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "closed"
    assert body["total_sessions"] == 1
    assert body["open_sessions"] == 0
    assert body["closed_sessions"] == 1
    assert body["total_coins"] == "0.00"
    assert body["total_bills"] == "20.00"
    assert body["total_counted"] == "20.00"


def test_cash_summary_report_accumulates_only_coins(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["coin_025"].id,
        "2026-07-01",
        4,
    )
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["coin_100"].id,
        "2026-07-02",
        3,
    )

    response = client.get(
        "/api/v1/reports/cash-summary",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_coins"] == "4.00"
    assert body["total_bills"] == "0.00"
    assert body["total_counted"] == body["total_coins"]


def test_cash_summary_report_accumulates_only_bills(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_1000"].id,
        "2026-07-01",
        2,
    )
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_2000"].id,
        "2026-07-02",
        1,
    )

    response = client.get(
        "/api/v1/reports/cash-summary",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_coins"] == "0.00"
    assert body["total_bills"] == "40.00"
    assert body["total_counted"] == body["total_bills"]


def test_cash_summary_report_returns_zeroes_when_filter_has_no_sessions(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_report_session(
        client,
        api_auth_headers,
        api_denominations["bill_1000"].id,
        "2026-07-01",
        2,
    )

    response = client.get(
        (
            "/api/v1/reports/cash-summary"
            "?date_from=2026-08-01&date_to=2026-08-31"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_sessions"] == 0
    assert body["total_coins"] == "0.00"
    assert body["total_bills"] == "0.00"
    assert body["total_counted"] == "0.00"
    assert body["total_pre_count_expenses"] == "0.00"
    assert body["total_post_count_expenses"] == "0.00"
    assert body["total_expenses"] == "0.00"
    assert body["final_total"] == "0.00"


def test_cash_summary_report_rejects_invalid_date_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        (
            "/api/v1/reports/cash-summary"
            "?date_from=2026-08-31&date_to=2026-08-01"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 400


def test_health_endpoint_stays_public(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/health")

    assert response.status_code == 200


def _create_report_session(
    client,
    headers: dict[str, str],
    denomination_id: int,
    session_date: str,
    quantity: int,
) -> int:
    cash_session_id = _create_cash_session(client, headers, session_date)
    _set_count(client, cash_session_id, denomination_id, quantity, headers)
    return cash_session_id


def _create_cash_session(
    client,
    headers: dict[str, str],
    session_date: str = "2026-07-01",
) -> int:
    response = client.post(
        "/api/v1/cash-sessions",
        headers=headers,
        json={"session_date": session_date},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _set_count(
    client,
    cash_session_id: int,
    denomination_id: int,
    quantity: int,
    headers: dict[str, str],
) -> None:
    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/count-items",
        headers=headers,
        json={"denomination_id": denomination_id, "quantity": quantity},
    )
    assert response.status_code == 200


def _create_expense(
    client,
    cash_session_id: int,
    amount: Decimal,
    headers: dict[str, str],
    expense_timing: str = "after_count",
) -> None:
    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=headers,
        json={
            "description": "Gasto de prueba",
            "amount": str(amount),
            "expense_timing": expense_timing,
        },
    )
    assert response.status_code == 201


def _close_cash_session(client, cash_session_id: int, headers: dict[str, str]) -> None:
    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/close",
        headers=headers,
    )
    assert response.status_code == 200
