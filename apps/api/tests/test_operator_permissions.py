import pytest


PERMISSION_DENIED_DETAIL = "No tienes permisos para realizar esta acción."


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/cash-sessions/999/corrections/count-items",
            {
                "denomination_id": 1,
                "quantity": 1,
                "reason": "Intento no autorizado",
            },
        ),
        (
            "POST",
            "/api/v1/sales/999/void",
            {"reason": "Intento no autorizado"},
        ),
        (
            "POST",
            "/api/v1/credit-payments/999/void",
            {"reason": "Intento no autorizado"},
        ),
        (
            "POST",
            "/api/v1/pricing/price-lists",
            {"name": "Lista no autorizada", "list_type": "general"},
        ),
        ("GET", "/api/v1/reports/management-dashboard", None),
        ("GET", "/api/v1/reports/exports/management-dashboard.xlsx", None),
        ("GET", "/api/v1/reports/exports/management-dashboard.pdf", None),
        ("GET", "/api/v1/users", None),
        ("GET", "/api/v1/employees", None),
        ("GET", "/api/v1/employees/attendance", None),
        ("GET", "/api/v1/payroll/runs", None),
        ("POST", "/api/v1/production/recipes", {}),
        ("POST", "/api/v1/production/batches/999/apply-inventory", {}),
        (
            "POST",
            "/api/v1/production/batches/999/material-consumption",
            {},
        ),
        (
            "POST",
            "/api/v1/inventory/locations",
            {"name": "Ubicación no autorizada"},
        ),
        (
            "POST",
            "/api/v1/inventory/movements/999/void",
            {"reason": "Intento no autorizado"},
        ),
    ],
)
def test_operator_receives_403_on_critical_endpoints(
    api_client,
    api_operator_auth_headers,
    method: str,
    path: str,
    payload,
) -> None:
    client, _ = api_client

    response = client.request(
        method,
        path,
        headers=api_operator_auth_headers,
        json=payload,
    )

    assert response.status_code == 403, (path, response.text)
    assert response.json()["detail"] == PERMISSION_DENIED_DETAIL


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("PATCH", "/api/v1/customers/999", {"name": "Cambio"}),
        ("POST", "/api/v1/products", {"name": "Producto"}),
        ("POST", "/api/v1/delivery-routes", {}),
        ("POST", "/api/v1/vehicles", {}),
        ("POST", "/api/v1/suppliers", {}),
        ("POST", "/api/v1/purchases", {}),
        ("POST", "/api/v1/operating-expenses", {}),
        ("POST", "/api/v1/route-loads", {}),
        ("POST", "/api/v1/route-returns", {}),
        ("POST", "/api/v1/route-closures", {}),
        ("POST", "/api/v1/route-cash-receipts", {}),
        ("GET", "/api/v1/reports/cash-summary", None),
        ("GET", "/api/v1/reports/monthly-operational-summary", None),
    ],
)
def test_operator_receives_403_on_unapproved_admin_writes_and_reports(
    api_client,
    api_operator_auth_headers,
    method: str,
    path: str,
    payload,
) -> None:
    client, _ = api_client

    response = client.request(
        method,
        path,
        headers=api_operator_auth_headers,
        json=payload,
    )

    assert response.status_code == 403, (path, response.text)


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/users",
        "/api/v1/employees",
        "/api/v1/employees/attendance",
        "/api/v1/payroll/runs",
        "/api/v1/pricing/price-lists",
    ],
)
def test_admin_auditor_can_access_restricted_families(
    api_client,
    api_auth_headers,
    path: str,
) -> None:
    client, _ = api_client

    response = client.get(path, headers=api_auth_headers)

    assert response.status_code == 200, (path, response.text)


def test_restricted_endpoint_uses_401_without_authentication(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/users")

    assert response.status_code == 401


def test_operator_can_create_customer_and_close_cash_session(
    api_client,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client

    customer = client.post(
        "/api/v1/customers",
        headers=api_operator_auth_headers,
        json={"name": "Cliente operativo"},
    )
    cash_session = client.post(
        "/api/v1/cash-sessions",
        headers=api_operator_auth_headers,
        json={"session_date": "2026-07-28", "notes": "Turno operativo"},
    )
    assert customer.status_code == 201, customer.text
    assert cash_session.status_code == 201, cash_session.text

    closed = client.post(
        f"/api/v1/cash-sessions/{cash_session.json()['id']}/close",
        headers=api_operator_auth_headers,
    )

    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"
    assert closed.json()["closed_at"] is not None


def test_operator_cannot_correct_closed_cash_session(
    api_client,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    cash_session = client.post(
        "/api/v1/cash-sessions",
        headers=api_operator_auth_headers,
        json={"session_date": "2026-07-27"},
    )
    assert cash_session.status_code == 201, cash_session.text

    cash_session_id = cash_session.json()["id"]
    closed = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/close",
        headers=api_operator_auth_headers,
    )

    correction = client.post(
        f"/api/v1/cash-sessions/{cash_session_id}/corrections/count-items",
        headers=api_operator_auth_headers,
        json={
            "denomination_id": 1,
            "quantity": 1,
            "reason": "Intento posterior al cierre",
        },
    )

    assert closed.status_code == 200
    assert correction.status_code == 403


def test_operator_can_register_production_and_operational_inventory_movements(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_admin_product(client, api_auth_headers)
    location = _create_admin_location(client, api_auth_headers)
    operator_id = client.get(
        "/api/v1/auth/me",
        headers=api_operator_auth_headers,
    ).json()["id"]

    production = client.post(
        "/api/v1/production/batches",
        headers=api_operator_auth_headers,
        json={
            "production_date": "2026-07-28",
            "items": [
                {
                    "product_id": product["id"],
                    "quantity_produced": "5",
                },
            ],
        },
    )
    entry = _create_operator_movement(
        client,
        api_operator_auth_headers,
        product["id"],
        location["id"],
        "entry",
        "3",
    )
    exit_movement = _create_operator_movement(
        client,
        api_operator_auth_headers,
        product["id"],
        location["id"],
        "exit",
        "1",
    )

    assert production.status_code == 201, production.text
    assert production.json()["created_by"] == operator_id
    assert entry.status_code == 201, entry.text
    assert entry.json()["created_by"] == operator_id
    assert exit_movement.status_code == 201, exit_movement.text
    assert exit_movement.json()["created_by"] == operator_id


@pytest.mark.parametrize("movement_type", ["adjustment_in", "adjustment_out"])
def test_operator_cannot_register_inventory_adjustments(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
    movement_type: str,
) -> None:
    client, _ = api_client
    product = _create_admin_product(client, api_auth_headers)
    location = _create_admin_location(client, api_auth_headers)

    response = client.post(
        "/api/v1/inventory/movements",
        headers=api_operator_auth_headers,
        json={
            "movement_date": "2026-07-28",
            "movement_type": movement_type,
            "product_id": product["id"],
            "location_id": location["id"],
            "quantity": "1",
            "reason": "Ajuste no autorizado",
        },
    )

    assert response.status_code == 403


def test_operator_cannot_set_inventory_unit_cost(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_admin_product(client, api_auth_headers)
    location = _create_admin_location(client, api_auth_headers)

    response = client.post(
        "/api/v1/inventory/movements",
        headers=api_operator_auth_headers,
        json={
            "movement_date": "2026-07-28",
            "movement_type": "entry",
            "product_id": product["id"],
            "location_id": location["id"],
            "quantity": "1",
            "unit_cost": "0.50",
            "reason": "Costo no autorizado",
        },
    )

    assert response.status_code == 403


def test_operator_can_register_credit_sale_and_payment(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_admin_product(client, api_auth_headers)
    customer = client.post(
        "/api/v1/customers",
        headers=api_operator_auth_headers,
        json={
            "name": "Cliente a crédito",
            "credit_allowed": True,
            "credit_limit": "0.00",
        },
    )
    assert customer.status_code == 201, customer.text

    listed_products = client.get(
        "/api/v1/products",
        headers=api_operator_auth_headers,
    )
    cash_sale = client.post(
        "/api/v1/sales/cash",
        headers=api_operator_auth_headers,
        json={
            "sale_date": "2026-07-28",
            "items": [{"product_id": product["id"], "quantity": "1"}],
        },
    )
    sale = client.post(
        "/api/v1/sales/credit",
        headers=api_operator_auth_headers,
        json={
            "sale_date": "2026-07-28",
            "customer_id": customer.json()["id"],
            "items": [{"product_id": product["id"], "quantity": "2"}],
        },
    )
    assert listed_products.status_code == 200, listed_products.text
    assert cash_sale.status_code == 201, cash_sale.text
    assert sale.status_code == 201, sale.text

    payment = client.post(
        f"/api/v1/sales/{sale.json()['id']}/payments",
        headers=api_operator_auth_headers,
        json={
            "payment_date": "2026-07-28",
            "amount": "1.00",
            "payment_method": "cash",
        },
    )

    assert payment.status_code == 201, payment.text


def _create_admin_product(client, headers) -> dict:
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": "PERM-BIDON-20L",
            "name": "Bidón permisos 20L",
            "category": "water",
            "unit": "container",
            "presentation": "20L",
            "default_price": "1.00",
            "cost_estimate": "0.40",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_admin_location(client, headers) -> dict:
    response = client.post(
        "/api/v1/inventory/locations",
        headers=headers,
        json={
            "code": "PERM-BODEGA",
            "name": "Bodega de permisos",
            "location_type": "warehouse",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_operator_movement(
    client,
    headers,
    product_id: int,
    location_id: int,
    movement_type: str,
    quantity: str,
):
    return client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "movement_date": "2026-07-28",
            "movement_type": movement_type,
            "product_id": product_id,
            "location_id": location_id,
            "quantity": quantity,
            "reason": "Movimiento operativo autorizado",
        },
    )
