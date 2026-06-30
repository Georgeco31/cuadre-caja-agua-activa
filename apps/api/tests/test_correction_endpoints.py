from decimal import Decimal


def test_normal_count_items_endpoint_stays_blocked_when_closed(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    _close_cash_session(client, cash_session_id, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": 1,
        },
    )

    assert response.status_code == 400


def test_normal_expenses_endpoint_stays_blocked_when_closed(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    _close_cash_session(client, cash_session_id, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/expenses",
        headers=api_auth_headers,
        json={"description": "Gasto cerrado", "amount": "1.00"},
    )

    assert response.status_code == 400


def test_correct_count_item_in_closed_cash_session(api_client, api_denominations, api_auth_headers) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    _set_count(client, cash_session_id, api_denominations["coin_025"].id, 4, api_auth_headers)
    _close_cash_session(client, cash_session_id, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": 8,
            "reason": "Se corrigio conteo de monedas de 25 centavos",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["count_item"]["quantity"] == 8
    assert body["count_item"]["subtotal"] == "2.00"
    assert body["summary"]["status"] == "closed"
    assert body["summary"]["final_total"] == "2.00"
    assert body["correction_log"]["previous_total"] == "1.00"
    assert body["correction_log"]["new_total"] == "2.00"
    assert body["correction_log"]["created_by"] is not None


def test_correct_count_item_rejects_empty_reason(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": 8,
            "reason": "   ",
        },
    )

    assert response.status_code == 400


def test_correct_count_item_rejects_negative_quantity(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": -1,
            "reason": "Cantidad corregida",
        },
    )

    assert response.status_code == 400


def test_correct_count_item_rejects_open_cash_session(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": 1,
            "reason": "Correccion anticipada",
        },
    )

    assert response.status_code == 400


def test_correct_count_item_returns_404_for_missing_cash_session(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/cash-sessions/999/corrections/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": 1,
            "reason": "Correccion de cuadre inexistente",
        },
    )

    assert response.status_code == 404


def test_correct_count_item_returns_404_for_missing_denomination(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": 999,
            "quantity": 1,
            "reason": "Correccion de denominacion inexistente",
        },
    )

    assert response.status_code == 404


def test_correct_count_item_registers_correction_log(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    correction_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/count-items",
        headers=api_auth_headers,
        json={
            "denomination_id": api_denominations["coin_025"].id,
            "quantity": 4,
            "reason": "Conteo encontrado despues del cierre",
        },
    )
    logs_response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections",
        headers=api_auth_headers,
    )

    assert correction_response.status_code == 200
    assert logs_response.status_code == 200
    assert logs_response.json() == [correction_response.json()["correction_log"]]


def test_corrective_expense_in_closed_cash_session(api_client, api_denominations, api_auth_headers) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    _set_count(client, cash_session_id, api_denominations["bill_1000"].id, 2, api_auth_headers)
    _close_cash_session(client, cash_session_id, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=api_auth_headers,
        json={
            "description": "Gasto olvidado de combustible",
            "amount": "5.00",
            "category": "Transporte",
            "expense_date": "2026-06-29",
            "notes": "Se olvido registrar al cierre",
            "reason": "Gasto detectado despues del cierre",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["expense"]["amount"] == "5.00"
    assert body["summary"]["status"] == "closed"
    assert body["summary"]["total_expenses"] == "5.00"
    assert body["summary"]["final_total"] == "15.00"
    assert body["correction_log"]["previous_total"] == "20.00"
    assert body["correction_log"]["new_total"] == "15.00"


def test_corrective_expense_rejects_non_positive_amount(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=api_auth_headers,
        json={
            "description": "Gasto invalido",
            "amount": "0.00",
            "reason": "Gasto detectado",
        },
    )

    assert response.status_code == 400


def test_corrective_expense_rejects_empty_description(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=api_auth_headers,
        json={
            "description": "  ",
            "amount": "1.00",
            "reason": "Gasto detectado",
        },
    )

    assert response.status_code == 400


def test_corrective_expense_rejects_empty_reason(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=api_auth_headers,
        json={
            "description": "Gasto olvidado",
            "amount": "1.00",
            "reason": " ",
        },
    )

    assert response.status_code == 400


def test_corrective_expense_rejects_open_cash_session(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)

    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=api_auth_headers,
        json={
            "description": "Gasto anticipado",
            "amount": "1.00",
            "reason": "Correccion anticipada",
        },
    )

    assert response.status_code == 400


def test_corrective_expense_registers_correction_log(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)

    correction_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=api_auth_headers,
        json={
            "description": "Gasto olvidado",
            "amount": "1.00",
            "reason": "Gasto detectado despues del cierre",
        },
    )
    logs_response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections",
        headers=api_auth_headers,
    )

    assert correction_response.status_code == 200
    assert logs_response.status_code == 200
    assert logs_response.json() == [correction_response.json()["correction_log"]]


def test_list_corrections_without_token_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/cash-sessions/1/corrections")

    assert response.status_code == 401


def test_list_corrections_returns_logs_for_cash_session(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_closed_cash_session(client, api_auth_headers)
    correction_response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=api_auth_headers,
        json={
            "description": "Gasto olvidado",
            "amount": "1.00",
            "reason": "Gasto detectado despues del cierre",
        },
    )

    response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections",
        headers=api_auth_headers,
    )

    assert correction_response.status_code == 200
    assert response.status_code == 200
    assert response.json() == [correction_response.json()["correction_log"]]


def test_list_corrections_does_not_mix_cash_sessions(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_cash_session_id = _create_closed_cash_session(
        client,
        api_auth_headers,
        session_date="2026-06-29",
    )
    second_cash_session_id = _create_closed_cash_session(
        client,
        api_auth_headers,
        session_date="2026-06-30",
    )
    first_response = _create_corrective_expense(
        client,
        first_cash_session_id,
        Decimal("1.00"),
        "Correccion del primer cuadre",
        api_auth_headers,
    )
    _create_corrective_expense(
        client,
        second_cash_session_id,
        Decimal("2.00"),
        "Correccion del segundo cuadre",
        api_auth_headers,
    )

    response = client.get(
        f"/api/v1/cash-sessions/{first_cash_session_id}/corrections",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == [first_response["correction_log"]]


def test_list_corrections_returns_404_for_missing_cash_session(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/cash-sessions/999/corrections",
        headers=api_auth_headers,
    )

    assert response.status_code == 404


def test_summary_after_corrections_reflects_new_total(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, _ = api_client
    cash_session_id = _create_cash_session(client, api_auth_headers)
    _set_count(client, cash_session_id, api_denominations["bill_1000"].id, 2, api_auth_headers)
    _close_cash_session(client, cash_session_id, api_auth_headers)
    _create_corrective_expense(
        client,
        cash_session_id,
        Decimal("5.00"),
        "Gasto detectado despues del cierre",
        api_auth_headers,
    )

    response = client.get(
        f"/api/v1/cash-sessions/{cash_session_id}/summary",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["final_total"] == "15.00"


def _create_cash_session(
    client,
    headers: dict[str, str],
    session_date: str = "2026-06-29",
) -> int:
    response = client.post(
        "/api/v1/cash-sessions",
        headers=headers,
        json={"session_date": session_date},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_closed_cash_session(
    client,
    headers: dict[str, str],
    session_date: str = "2026-06-29",
) -> int:
    cash_session_id = _create_cash_session(client, headers, session_date)
    _close_cash_session(client, cash_session_id, headers)
    return cash_session_id


def _close_cash_session(client, cash_session_id: int, headers: dict[str, str]) -> None:
    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/close",
        headers=headers,
    )
    assert response.status_code == 200


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


def _create_corrective_expense(
    client,
    cash_session_id: int,
    amount: Decimal,
    reason: str,
    headers: dict[str, str],
):
    response = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/expenses",
        headers=headers,
        json={
            "description": "Gasto olvidado",
            "amount": str(amount),
            "reason": reason,
        },
    )
    assert response.status_code == 200
    return response.json()
