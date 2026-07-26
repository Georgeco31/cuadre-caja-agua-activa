from decimal import Decimal

from app.models.denomination import Denomination
from app.seeds.admin_user import seed_admin_user


def test_login_with_valid_credentials_returns_bearer_token(api_client) -> None:
    client, testing_session_local = api_client
    _seed_admin(testing_session_local)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["role"] == "admin_auditor"


def test_login_with_unknown_username_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "missing", "password": "admin123"},
    )

    assert response.status_code == 401


def test_login_with_wrong_password_returns_401(api_client) -> None:
    client, testing_session_local = api_client
    _seed_admin(testing_session_local)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_login_with_inactive_user_returns_403(api_client) -> None:
    client, testing_session_local = api_client
    _seed_admin(testing_session_local, is_active=False)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 403


def test_auth_me_with_valid_token_returns_current_user(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get("/api/v1/auth/me", headers=api_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin_auditor"
    assert body["is_active"] is True
    assert "password_hash" not in body


def test_auth_me_without_token_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_auth_me_with_invalid_token_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_health_endpoint_stays_public(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "cuadre-caja-api"}


def test_protected_cash_sessions_endpoint_without_token_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/cash-sessions")

    assert response.status_code == 401


def test_protected_cash_sessions_endpoint_with_token_works(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get("/api/v1/cash-sessions", headers=api_auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_denominations_endpoint_without_token_returns_401(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/denominations")

    assert response.status_code == 401


def test_denominations_endpoint_with_token_returns_list(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    with testing_session_local() as session:
        session.add(
            Denomination(
                type="coin",
                value=Decimal("0.25"),
                label="Moneda de 25 centavos",
                is_active=True,
            ),
        )
        session.commit()

    response = client.get("/api/v1/denominations", headers=api_auth_headers)

    assert response.status_code == 200
    assert response.json()[0]["label"] == "Moneda de 25 centavos"


def _seed_admin(testing_session_local, is_active: bool = True) -> None:
    with testing_session_local() as session:
        seed_admin_user(
            db=session,
            username="admin",
            password="admin123",
            is_active=is_active,
        )
