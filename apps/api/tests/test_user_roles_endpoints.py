from app.security.tokens import decode_access_token


def test_login_token_contains_role(api_client, api_operator_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "operator", "password": "operator123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "operator"
    assert decode_access_token(body["access_token"])["role"] == "operator"


def test_admin_lists_users_without_password_hash(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get("/api/v1/users", headers=api_auth_headers)

    assert response.status_code == 200
    assert response.json()[0]["role"] == "admin_auditor"
    assert "password_hash" not in response.json()[0]


def test_operator_cannot_list_or_create_users(
    api_client,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client

    listed = client.get("/api/v1/users", headers=api_operator_auth_headers)
    created = client.post(
        "/api/v1/users",
        headers=api_operator_auth_headers,
        json={
            "username": "blocked",
            "password": "blocked123",
            "role": "operator",
        },
    )

    assert listed.status_code == 403
    assert created.status_code == 403
    assert listed.json()["detail"] == "No tienes permisos para realizar esta acción."


def test_admin_creates_operator_and_rejects_duplicate_username(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    payload = {
        "username": "secretaria",
        "password": "ClaveSegura123",
        "role": "operator",
        "is_active": True,
    }

    created = client.post("/api/v1/users", headers=api_auth_headers, json=payload)
    duplicate = client.post("/api/v1/users", headers=api_auth_headers, json=payload)

    assert created.status_code == 201
    assert created.json()["role"] == "operator"
    assert created.json()["is_active"] is True
    assert "password_hash" not in created.json()
    assert duplicate.status_code == 409


def test_new_user_defaults_to_operator(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/users",
        headers=api_auth_headers,
        json={"username": "secretaria", "password": "ClaveSegura123"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "operator"


def test_user_validation_rejects_short_password_and_invalid_role(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    short_password = client.post(
        "/api/v1/users",
        headers=api_auth_headers,
        json={"username": "short", "password": "1234567"},
    )
    invalid_role = client.post(
        "/api/v1/users",
        headers=api_auth_headers,
        json={
            "username": "other",
            "password": "ClaveSegura123",
            "role": "superadmin",
        },
    )

    assert short_password.status_code == 422
    assert invalid_role.status_code == 422


def test_admin_changes_role_and_status(api_client, api_auth_headers) -> None:
    client, _ = api_client
    created = _create_operator(client, api_auth_headers)

    promoted = client.patch(
        f"/api/v1/users/{created['id']}",
        headers=api_auth_headers,
        json={"role": "admin_auditor"},
    )
    deactivated = client.patch(
        f"/api/v1/users/{created['id']}/deactivate",
        headers=api_auth_headers,
    )
    activated = client.patch(
        f"/api/v1/users/{created['id']}/activate",
        headers=api_auth_headers,
    )

    assert promoted.status_code == 200
    assert promoted.json()["role"] == "admin_auditor"
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False
    assert activated.status_code == 200
    assert activated.json()["is_active"] is True


def test_cannot_deactivate_or_demote_last_active_admin(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    admin_id = client.get("/api/v1/auth/me", headers=api_auth_headers).json()["id"]

    deactivated = client.patch(
        f"/api/v1/users/{admin_id}/deactivate",
        headers=api_auth_headers,
    )
    demoted = client.patch(
        f"/api/v1/users/{admin_id}",
        headers=api_auth_headers,
        json={"role": "operator"},
    )

    assert deactivated.status_code == 400
    assert demoted.status_code == 400
    assert "admin_auditor activo" in deactivated.json()["detail"]


def test_admin_changes_user_password(api_client, api_auth_headers) -> None:
    client, _ = api_client
    created = _create_operator(client, api_auth_headers)

    changed = client.patch(
        f"/api/v1/users/{created['id']}/password",
        headers=api_auth_headers,
        json={"new_password": "NuevaClaveSegura123"},
    )
    old_login = client.post(
        "/api/v1/auth/login",
        json={"username": "secretaria", "password": "ClaveSegura123"},
    )
    new_login = client.post(
        "/api/v1/auth/login",
        json={"username": "secretaria", "password": "NuevaClaveSegura123"},
    )

    assert changed.status_code == 200
    assert "password_hash" not in changed.json()
    assert old_login.status_code == 401
    assert new_login.status_code == 200


def test_operator_can_use_normal_cash_session_endpoints(
    api_client,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client

    created = client.post(
        "/api/v1/cash-sessions",
        headers=api_operator_auth_headers,
        json={"session_date": "2026-07-25", "notes": "Operacion normal"},
    )
    listed = client.get(
        "/api/v1/cash-sessions",
        headers=api_operator_auth_headers,
    )

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == created.json()["id"]


def test_operator_cannot_use_critical_endpoints(
    api_client,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    critical_requests = [
        (
            "post",
            "/api/v1/sales/999/void",
            {"reason": "No autorizado"},
        ),
        (
            "post",
            "/api/v1/cash-sessions/999/corrections/count-items",
            {
                "denomination_id": 1,
                "quantity": 1,
                "reason": "No autorizado",
            },
        ),
        (
            "post",
            "/api/v1/purchases/999/void",
            {"reason": "No autorizado"},
        ),
        (
            "post",
            "/api/v1/operating-expenses/999/void",
            {"reason": "No autorizado"},
        ),
        (
            "post",
            "/api/v1/production/batches/999/void",
            {"reason": "No autorizado"},
        ),
        (
            "post",
            "/api/v1/pricing/price-lists",
            {"name": "No autorizada", "list_type": "general"},
        ),
    ]

    for method, path, payload in critical_requests:
        response = client.request(
            method,
            path,
            headers=api_operator_auth_headers,
            json=payload,
        )
        assert response.status_code == 403, (path, response.text)


def test_operator_cannot_access_management_or_exports(
    api_client,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client

    dashboard = client.get(
        "/api/v1/reports/management-dashboard",
        headers=api_operator_auth_headers,
    )
    export = client.get(
        "/api/v1/reports/exports/management-dashboard.xlsx",
        headers=api_operator_auth_headers,
    )

    assert dashboard.status_code == 403
    assert export.status_code == 403


def _create_operator(client, headers: dict[str, str]) -> dict[str, object]:
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": "secretaria",
            "password": "ClaveSegura123",
            "role": "operator",
        },
    )
    assert response.status_code == 201
    return response.json()
