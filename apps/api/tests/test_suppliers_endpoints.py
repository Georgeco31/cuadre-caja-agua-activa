import importlib.util
from pathlib import Path

import pytest

from app.models.supplier import Supplier


def test_create_supplier(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/suppliers",
        headers=api_auth_headers,
        json={
            "name": " Proveedor de botellones ",
            "identification": " 0999999999001 ",
            "primary_phone": " 0999999999 ",
            "secondary_phone": " 052000000 ",
            "email": " proveedor@example.com ",
            "address": " Manta ",
            "contact_name": " Juan Perez ",
            "supplier_type": " insumos ",
            "payment_terms": " contado ",
            "notes": " Proveedor principal ",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Proveedor de botellones"
    assert body["identification"] == "0999999999001"
    assert body["primary_phone"] == "0999999999"
    assert body["supplier_type"] == "insumos"
    assert body["payment_terms"] == "contado"
    assert body["is_active"] is True
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


@pytest.mark.parametrize("payload", [{}, {"name": "   "}, {"name": None}])
def test_create_supplier_requires_name(
    api_client,
    api_auth_headers,
    payload,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/suppliers",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_supplier_identification_must_be_unique(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_supplier(
        client,
        api_auth_headers,
        name="Proveedor uno",
        identification="0990000000001",
    )

    response = client.post(
        "/api/v1/suppliers",
        headers=api_auth_headers,
        json={
            "name": "Proveedor dos",
            "identification": " 0990000000001 ",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "La identificacion del proveedor ya esta registrada."
    )


def test_supplier_identification_can_be_empty_for_multiple_records(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    first = _create_supplier(
        client,
        api_auth_headers,
        name="Sin identificacion uno",
        identification="   ",
    )
    second = _create_supplier(
        client,
        api_auth_headers,
        name="Sin identificacion dos",
        identification=None,
    )

    assert first["identification"] is None
    assert second["identification"] is None


def test_list_and_filter_suppliers(api_client, api_auth_headers) -> None:
    client, _ = api_client
    active = _create_supplier(
        client,
        api_auth_headers,
        name="Botellones Manta",
        identification="SUP-001",
        supplier_type="insumos",
        contact_name="Maria",
    )
    inactive = _create_supplier(
        client,
        api_auth_headers,
        name="Taller Central",
        identification="SUP-002",
        supplier_type="mantenimiento",
    )
    client.patch(
        f"/api/v1/suppliers/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    all_response = client.get("/api/v1/suppliers", headers=api_auth_headers)
    search_response = client.get(
        "/api/v1/suppliers",
        headers=api_auth_headers,
        params={"search": "maria"},
    )
    active_response = client.get(
        "/api/v1/suppliers",
        headers=api_auth_headers,
        params={"is_active": "true"},
    )
    type_response = client.get(
        "/api/v1/suppliers",
        headers=api_auth_headers,
        params={"supplier_type": "mantenimiento"},
    )

    assert all_response.status_code == 200
    assert [item["name"] for item in all_response.json()] == [
        "Botellones Manta",
        "Taller Central",
    ]
    assert [item["id"] for item in search_response.json()] == [active["id"]]
    assert [item["id"] for item in active_response.json()] == [active["id"]]
    assert [item["id"] for item in type_response.json()] == [inactive["id"]]


def test_get_update_deactivate_and_activate_supplier(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    supplier = _create_supplier(
        client,
        api_auth_headers,
        name="Proveedor original",
        identification="SUP-EDIT",
    )

    detail_response = client.get(
        f"/api/v1/suppliers/{supplier['id']}",
        headers=api_auth_headers,
    )
    update_response = client.patch(
        f"/api/v1/suppliers/{supplier['id']}",
        headers=api_auth_headers,
        json={
            "name": "Proveedor actualizado",
            "supplier_type": "servicios",
            "payment_terms": "credito 15 dias",
        },
    )
    deactivate_response = client.patch(
        f"/api/v1/suppliers/{supplier['id']}/deactivate",
        headers=api_auth_headers,
    )
    activate_response = client.patch(
        f"/api/v1/suppliers/{supplier['id']}/activate",
        headers=api_auth_headers,
    )

    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == supplier["id"]
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Proveedor actualizado"
    assert update_response.json()["supplier_type"] == "servicios"
    assert deactivate_response.json()["is_active"] is False
    assert activate_response.json()["is_active"] is True
    with testing_session_local() as session:
        assert session.get(Supplier, supplier["id"]) is not None


def test_supplier_detail_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get("/api/v1/suppliers/999", headers=api_auth_headers)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/suppliers", {"name": "Proveedor"}),
        ("GET", "/api/v1/suppliers", None),
        ("GET", "/api/v1/suppliers/1", None),
        ("PATCH", "/api/v1/suppliers/1", {"name": "Proveedor"}),
        ("PATCH", "/api/v1/suppliers/1/deactivate", None),
        ("PATCH", "/api/v1/suppliers/1/activate", None),
    ],
)
def test_supplier_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_purchase_migration_creates_only_base_tables(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0019_create_suppliers_purchases.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0019_purchases",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[str] = []

    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *elements: created_tables.append(table_name),
    )
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)

    migration.upgrade()

    assert migration.revision == "0019_purchases"
    assert migration.down_revision == "0018_route_receipts"
    assert len(migration.revision) <= 32
    assert created_tables == ["suppliers", "purchases", "purchase_items"]


def _create_supplier(client, headers: dict[str, str], **overrides):
    payload = {
        "name": "Proveedor Agua Activa",
        "supplier_type": "general",
        "payment_terms": "contado",
        **overrides,
    }
    response = client.post("/api/v1/suppliers", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()
