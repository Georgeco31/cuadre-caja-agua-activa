import importlib.util
from pathlib import Path

import pytest

from app.models.customer import Customer


def test_create_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/customers",
        headers=api_auth_headers,
        json={
            "name": "Tienda Don Luis",
            "primary_phone": "0999999999",
            "secondary_phone": "022222222",
            "address": "Barrio Centro",
            "sector": "Centro",
            "customer_type": "store",
            "route_reference": "Ruta Centro",
            "credit_allowed": True,
            "credit_limit": "50.00",
            "notes": "Cliente frecuente",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Tienda Don Luis"
    assert body["customer_type"] == "store"
    assert body["credit_limit"] == "50.00"
    assert body["is_active"] is True
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_create_customer_requires_name(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/customers",
        headers=api_auth_headers,
        json={"primary_phone": "0999999999"},
    )

    assert response.status_code == 422


def test_create_customer_rejects_blank_name(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/customers",
        headers=api_auth_headers,
        json={"name": "   "},
    )

    assert response.status_code == 422


def test_create_customer_rejects_negative_credit_limit(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/customers",
        headers=api_auth_headers,
        json={"name": "Cliente", "credit_limit": "-0.01"},
    )

    assert response.status_code == 422


def test_create_customer_rejects_duplicate_primary_phone(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_customer(
        client,
        api_auth_headers,
        name="Primer cliente",
        primary_phone="0999999999",
    )

    response = client.post(
        "/api/v1/customers",
        headers=api_auth_headers,
        json={"name": "Segundo cliente", "primary_phone": " 0999999999 "},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "El telefono principal ya esta registrado."
    )


def test_list_customers(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_customer(client, api_auth_headers, name="Tienda Norte")
    _create_customer(client, api_auth_headers, name="Casa Centro")

    response = client.get("/api/v1/customers", headers=api_auth_headers)

    assert response.status_code == 200
    assert [customer["name"] for customer in response.json()] == [
        "Casa Centro",
        "Tienda Norte",
    ]


@pytest.mark.parametrize("search", ["luis", "0987654321", "sur", "store"])
def test_list_customers_filters_by_search(
    api_client,
    api_auth_headers,
    search: str,
) -> None:
    client, _ = api_client
    _create_customer(
        client,
        api_auth_headers,
        name="Tienda Don Luis",
        primary_phone="0987654321",
        secondary_phone="022222222",
        sector="Sur",
        customer_type="store",
    )
    _create_customer(
        client,
        api_auth_headers,
        name="Casa Maria",
        primary_phone="0911111111",
        sector="Norte",
        customer_type="household",
    )

    response = client.get(
        "/api/v1/customers",
        headers=api_auth_headers,
        params={"search": search},
    )

    assert response.status_code == 200
    assert [customer["name"] for customer in response.json()] == [
        "Tienda Don Luis"
    ]


def test_list_customers_filters_by_active_status(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    active = _create_customer(client, api_auth_headers, name="Cliente activo")
    inactive = _create_customer(client, api_auth_headers, name="Cliente inactivo")
    client.patch(
        f"/api/v1/customers/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.get(
        "/api/v1/customers",
        headers=api_auth_headers,
        params={"is_active": "true"},
    )

    assert response.status_code == 200
    assert [customer["id"] for customer in response.json()] == [active["id"]]


def test_list_customers_filters_by_customer_type(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_customer(
        client,
        api_auth_headers,
        name="Tienda",
        customer_type="store",
    )
    _create_customer(
        client,
        api_auth_headers,
        name="Casa",
        customer_type="household",
    )

    response = client.get(
        "/api/v1/customers",
        headers=api_auth_headers,
        params={"customer_type": "store"},
    )

    assert response.status_code == 200
    assert [customer["name"] for customer in response.json()] == ["Tienda"]


def test_list_customers_filters_by_sector(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_customer(client, api_auth_headers, name="Cliente centro", sector="Centro")
    _create_customer(client, api_auth_headers, name="Cliente norte", sector="Norte")

    response = client.get(
        "/api/v1/customers",
        headers=api_auth_headers,
        params={"sector": "centro"},
    )

    assert response.status_code == 200
    assert [customer["name"] for customer in response.json()] == [
        "Cliente centro"
    ]


def test_get_customer_detail(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_customer(client, api_auth_headers, name="Cliente detalle")

    response = client.get(
        f"/api/v1/customers/{customer['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == customer


def test_get_customer_detail_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get("/api/v1/customers/999", headers=api_auth_headers)

    assert response.status_code == 404


def test_update_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_customer(
        client,
        api_auth_headers,
        name="Cliente original",
        sector="Norte",
        credit_limit="0.00",
    )

    response = client.patch(
        f"/api/v1/customers/{customer['id']}",
        headers=api_auth_headers,
        json={
            "name": "Cliente actualizado",
            "sector": "Centro",
            "credit_allowed": True,
            "credit_limit": "75.50",
            "notes": "Datos revisados",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Cliente actualizado"
    assert body["sector"] == "Centro"
    assert body["credit_allowed"] is True
    assert body["credit_limit"] == "75.50"
    assert body["notes"] == "Datos revisados"


def test_deactivate_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_customer(client, api_auth_headers, name="Cliente")

    response = client.patch(
        f"/api/v1/customers/{customer['id']}/deactivate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_reactivate_customer(api_client, api_auth_headers) -> None:
    client, _ = api_client
    customer = _create_customer(client, api_auth_headers, name="Cliente")
    client.patch(
        f"/api/v1/customers/{customer['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.patch(
        f"/api/v1/customers/{customer['id']}/activate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_deactivate_customer_does_not_delete_record(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    customer = _create_customer(client, api_auth_headers, name="Cliente persistente")

    client.patch(
        f"/api/v1/customers/{customer['id']}/deactivate",
        headers=api_auth_headers,
    )

    with testing_session_local() as session:
        stored_customer = session.get(Customer, customer["id"])
        assert stored_customer is not None
        assert stored_customer.is_active is False


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/customers", {"name": "Cliente"}),
        ("GET", "/api/v1/customers", None),
        ("GET", "/api/v1/customers/1", None),
        ("PATCH", "/api/v1/customers/1", {"name": "Cliente"}),
        ("PATCH", "/api/v1/customers/1/deactivate", None),
        ("PATCH", "/api/v1/customers/1/activate", None),
    ],
)
def test_customer_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, str] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_customer_migration_creates_customers_table(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0003_create_customers.py"
    )
    spec = importlib.util.spec_from_file_location("migration_0003_customers", migration_path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[tuple[str, tuple[object, ...]]] = []

    def record_create_table(table_name: str, *elements: object) -> None:
        created_tables.append((table_name, elements))

    monkeypatch.setattr(migration.op, "create_table", record_create_table)

    migration.upgrade()

    assert migration.revision == "0003_customers"
    assert migration.down_revision == "0002_expense_timing"
    assert len(migration.revision) <= 32
    assert [table_name for table_name, _ in created_tables] == ["customers"]
    column_names = {
        element.name
        for element in created_tables[0][1]
        if element.__class__.__name__ == "Column"
    }
    assert column_names == {
        "id",
        "name",
        "primary_phone",
        "secondary_phone",
        "address",
        "sector",
        "customer_type",
        "route_reference",
        "credit_allowed",
        "credit_limit",
        "is_active",
        "notes",
        "created_at",
        "updated_at",
    }


def _create_customer(client, headers: dict[str, str], **overrides):
    payload = {
        "name": "Cliente Agua Activa",
        "customer_type": "household",
        "credit_allowed": False,
        "credit_limit": "0.00",
        **overrides,
    }
    response = client.post("/api/v1/customers", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()
