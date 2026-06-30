from decimal import Decimal


def test_create_cash_session_endpoint(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json={
            "session_date": "2026-06-29",
            "notes": "Cuadre diario Agua Activa",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["session_date"] == "2026-06-29"
    assert body["status"] == "open"
    assert body["notes"] == "Cuadre diario Agua Activa"
    assert body["created_by"] is None
    assert body["closed_at"] is None


def test_create_cash_session_endpoint_rejects_duplicate_date(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    payload = {"session_date": "2026-06-29"}

    first_response = client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json=payload,
    )
    duplicate_response = client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json=payload,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_list_cash_sessions_endpoint(api_client, api_auth_headers) -> None:
    client, _ = api_client
    client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json={"session_date": "2026-06-29"},
    )
    client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json={"session_date": "2026-06-30"},
    )

    response = client.get("/api/v1/cash-sessions", headers=api_auth_headers)

    assert response.status_code == 200
    assert [item["session_date"] for item in response.json()] == [
        "2026-06-29",
        "2026-06-30",
    ]


def test_get_cash_session_by_id_endpoint(api_client, api_auth_headers) -> None:
    client, _ = api_client
    create_response = client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json={"session_date": "2026-06-29"},
    )
    cash_session_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == cash_session_id


def test_get_cash_session_by_id_endpoint_returns_404(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get("/api/v1/cash-sessions/999", headers=api_auth_headers)

    assert response.status_code == 404


def test_get_cash_session_by_date_endpoint(api_client, api_auth_headers) -> None:
    client, _ = api_client
    client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json={"session_date": "2026-06-29"},
    )

    response = client.get(
        "/api/v1/cash-sessions/by-date/2026-06-29",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["session_date"] == "2026-06-29"


def test_count_items_endpoint_creates_and_updates_item(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    denomination_id = api_denominations["coin_025"].id

    create_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/count-items",
        headers=api_auth_headers,
        json={"denomination_id": denomination_id, "quantity": 10},
    )
    update_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/count-items",
        headers=api_auth_headers,
        json={"denomination_id": denomination_id, "quantity": 12},
    )

    assert create_response.status_code == 200
    assert create_response.json()["subtotal"] == "2.50"
    assert update_response.status_code == 200
    assert update_response.json()["id"] == create_response.json()["id"]
    assert update_response.json()["quantity"] == 12
    assert update_response.json()["subtotal"] == "3.00"


def test_count_items_endpoint_rejects_negative_quantity(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": -1,
        },
    )

    assert response.status_code == 400


def test_expenses_endpoint_creates_expense(api_client, api_auth_headers) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=api_auth_headers,
        json={
            "description": "Compra de fundas",
            "amount": "8.50",
            "category": "Insumos",
            "expense_date": "2026-06-29",
            "notes": "Gasto hecho con dinero de caja",
        },
    )

    assert response.status_code == 201
    assert response.json()["amount"] == "8.50"
    assert response.json()["expense_date"] == "2026-06-29"


def test_expenses_endpoint_rejects_non_positive_amount(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=api_auth_headers,
        json={"description": "Gasto invalido", "amount": "0.00"},
    )

    assert response.status_code == 400


def test_list_expenses_endpoint_without_token_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/cash-sessions/1/expenses")

    assert response.status_code == 401


def test_list_expenses_endpoint_returns_expenses(api_client, api_auth_headers) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    _create_expense(client, cash_session_id, Decimal("8.50"), api_auth_headers)
    _create_expense(client, cash_session_id, Decimal("2.00"), api_auth_headers)

    response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert [expense["amount"] for expense in response.json()] == ["8.50", "2.00"]


def test_list_expenses_endpoint_returns_404_for_missing_cash_session(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/cash-sessions/999/expenses",
        headers=api_auth_headers,
    )

    assert response.status_code == 404


def test_create_and_list_expense_returns_created_expense(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    create_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=api_auth_headers,
        json={
            "description": "Compra de fundas",
            "amount": "8.50",
            "category": "Insumos",
            "expense_date": "2026-06-29",
            "notes": "Gasto hecho con dinero de caja",
        },
    )

    response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=api_auth_headers,
    )

    assert create_response.status_code == 201
    assert response.status_code == 200
    assert response.json() == [create_response.json()]


def test_list_expenses_endpoint_does_not_mix_cash_sessions(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_cash_session_id = _create_cash_session(client, api_auth_headers)
    second_response = client.post(
        "/api/v1/cash-sessions",
        headers=api_auth_headers,
        json={"session_date": "2026-06-30"},
    )
    second_cash_session_id = second_response.json()["id"]
    _create_expense(client, first_cash_session_id, Decimal("8.50"), api_auth_headers)
    _create_expense(client, second_cash_session_id, Decimal("2.00"), api_auth_headers)

    response = client.get(
        f"/api/v1/cash-sessions/{first_cash_session_id}/expenses",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert [expense["amount"] for expense in response.json()] == ["8.50"]


def test_summary_endpoint_calculates_totals(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)

    _set_count(client, cash_session_id, api_denominations["coin_025"].id, 10, api_auth_headers)
    _set_count(client, cash_session_id, api_denominations["coin_100"].id, 5, api_auth_headers)
    _set_count(client, cash_session_id, api_denominations["bill_1000"].id, 3, api_auth_headers)
    _set_count(client, cash_session_id, api_denominations["bill_2000"].id, 2, api_auth_headers)
    _create_expense(client, cash_session_id, Decimal("8.50"), api_auth_headers)
    _create_expense(client, cash_session_id, Decimal("2.00"), api_auth_headers)

    response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/summary",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "cash_session_id": cash_session_id,
        "session_date": "2026-06-29",
        "status": "open",
        "total_coins": "7.50",
        "total_bills": "70.00",
        "total_counted": "77.50",
        "total_expenses": "10.50",
        "final_total": "67.00",
    }


def test_close_cash_session_endpoint_blocks_later_changes(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)

    close_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/close",
        headers=api_auth_headers,
    )
    count_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": 1,
        },
    )
    expense_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=api_auth_headers,
        json={"description": "Gasto cerrado", "amount": "1.00"},
    )

    assert close_response.status_code == 200
    assert close_response.json()["status"] == "closed"
    assert close_response.json()["closed_at"] is not None
    assert count_response.status_code == 400
    assert expense_response.status_code == 400


def _create_cash_session(client, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/cash-sessions",
        headers=headers,
        json={"session_date": "2026-06-29"},
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
) -> None:
    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=headers,
        json={"description": "Gasto", "amount": str(amount)},
    )
    assert response.status_code == 201
