import importlib.util
from pathlib import Path

import pytest

from app.models.delivery_route import DeliveryRoute


def test_create_delivery_route(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        json={
            "code": "RUTA-CENTRO",
            "name": "Ruta Centro",
            "description": "Ruta principal del centro de Manta",
            "zone": "Manta",
            "sector": "Centro",
            "service_days": "lunes, miércoles, viernes",
            "reference_driver": "Pedro Zambrano",
            "reference_vehicle": "Camión 1",
            "expected_daily_cash": "115.00",
            "notes": "Ruta con clientes frecuentes",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["code"] == "RUTA-CENTRO"
    assert body["name"] == "Ruta Centro"
    assert body["zone"] == "Manta"
    assert body["sector"] == "Centro"
    assert body["reference_driver"] == "Pedro Zambrano"
    assert body["reference_vehicle"] == "Camión 1"
    assert body["expected_daily_cash"] == "115.00"
    assert body["is_active"] is True
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_create_delivery_route_requires_name(api_client, api_auth_headers) -> None:
    client, _ = api_client
    payload = _delivery_route_payload()
    payload.pop("name")

    response = client.post(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_create_delivery_route_rejects_blank_name(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        json=_delivery_route_payload(name="   "),
    )

    assert response.status_code == 422


def test_create_delivery_route_rejects_negative_expected_cash(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        json=_delivery_route_payload(expected_daily_cash="-0.01"),
    )

    assert response.status_code == 422


def test_create_delivery_route_rejects_duplicate_code(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_delivery_route(client, api_auth_headers, code="RUTA-CENTRO")

    response = client.post(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        json=_delivery_route_payload(name="Otra ruta", code="RUTA-CENTRO"),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "El codigo de ruta ya esta registrado."


def test_create_delivery_route_allows_blank_or_null_code(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    first = _create_delivery_route(
        client,
        api_auth_headers,
        name="Ruta sin código",
        code="   ",
    )
    second = _create_delivery_route(
        client,
        api_auth_headers,
        name="Segunda ruta sin código",
        code=None,
    )

    assert first["code"] is None
    assert second["code"] is None


def test_list_delivery_routes(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_delivery_route(client, api_auth_headers, name="Ruta Sur")
    _create_delivery_route(client, api_auth_headers, name="Ruta Centro")

    response = client.get("/api/v1/delivery-routes", headers=api_auth_headers)

    assert response.status_code == 200
    assert [route["name"] for route in response.json()] == ["Ruta Centro", "Ruta Sur"]


@pytest.mark.parametrize(
    "search",
    ["Ruta Centro", "RUTA-CENTRO", "Manta", "Tarqui", "miércoles"],
)
def test_list_delivery_routes_searches_expected_fields(
    api_client,
    api_auth_headers,
    search: str,
) -> None:
    client, _ = api_client
    _create_delivery_route(
        client,
        api_auth_headers,
        code="RUTA-CENTRO",
        name="Ruta Centro",
        zone="Manta",
        sector="Tarqui",
        service_days="lunes, miércoles, viernes",
    )
    _create_delivery_route(
        client,
        api_auth_headers,
        code="RUTA-NORTE",
        name="Ruta Norte",
        zone="Montecristi",
        sector="Colorado",
        service_days="martes y jueves",
    )

    response = client.get(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        params={"search": search},
    )

    assert response.status_code == 200
    assert [route["name"] for route in response.json()] == ["Ruta Centro"]


def test_list_delivery_routes_filters_by_active_status(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    active = _create_delivery_route(client, api_auth_headers, name="Ruta activa")
    inactive = _create_delivery_route(client, api_auth_headers, name="Ruta inactiva")
    client.patch(
        f"/api/v1/delivery-routes/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.get(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        params={"is_active": "true"},
    )

    assert response.status_code == 200
    assert [route["id"] for route in response.json()] == [active["id"]]


def test_list_delivery_routes_filters_by_zone(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_delivery_route(client, api_auth_headers, name="Ruta Manta", zone="Manta")
    _create_delivery_route(
        client,
        api_auth_headers,
        name="Ruta Montecristi",
        zone="Montecristi",
    )

    response = client.get(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        params={"zone": "manta"},
    )

    assert response.status_code == 200
    assert [route["name"] for route in response.json()] == ["Ruta Manta"]


def test_list_delivery_routes_filters_by_sector(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_delivery_route(client, api_auth_headers, name="Ruta Centro", sector="Centro")
    _create_delivery_route(client, api_auth_headers, name="Ruta Sur", sector="Los Esteros")

    response = client.get(
        "/api/v1/delivery-routes",
        headers=api_auth_headers,
        params={"sector": "centro"},
    )

    assert response.status_code == 200
    assert [route["name"] for route in response.json()] == ["Ruta Centro"]


def test_get_delivery_route_detail(api_client, api_auth_headers) -> None:
    client, _ = api_client
    delivery_route = _create_delivery_route(client, api_auth_headers)

    response = client.get(
        f"/api/v1/delivery-routes/{delivery_route['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == delivery_route


def test_get_delivery_route_detail_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get("/api/v1/delivery-routes/999", headers=api_auth_headers)

    assert response.status_code == 404


def test_update_delivery_route(api_client, api_auth_headers) -> None:
    client, _ = api_client
    delivery_route = _create_delivery_route(
        client,
        api_auth_headers,
        name="Ruta original",
        expected_daily_cash="100.00",
    )

    response = client.patch(
        f"/api/v1/delivery-routes/{delivery_route['id']}",
        headers=api_auth_headers,
        json={
            "name": "Ruta actualizada",
            "zone": "Manta",
            "sector": "Centro",
            "service_days": "lunes a viernes",
            "expected_daily_cash": "125.50",
            "notes": "Datos revisados",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ruta actualizada"
    assert body["zone"] == "Manta"
    assert body["sector"] == "Centro"
    assert body["service_days"] == "lunes a viernes"
    assert body["expected_daily_cash"] == "125.50"
    assert body["notes"] == "Datos revisados"


def test_deactivate_delivery_route(api_client, api_auth_headers) -> None:
    client, _ = api_client
    delivery_route = _create_delivery_route(client, api_auth_headers)

    response = client.patch(
        f"/api/v1/delivery-routes/{delivery_route['id']}/deactivate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_reactivate_delivery_route(api_client, api_auth_headers) -> None:
    client, _ = api_client
    delivery_route = _create_delivery_route(client, api_auth_headers)
    client.patch(
        f"/api/v1/delivery-routes/{delivery_route['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.patch(
        f"/api/v1/delivery-routes/{delivery_route['id']}/activate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_deactivate_delivery_route_does_not_delete_record(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    delivery_route = _create_delivery_route(client, api_auth_headers)

    client.patch(
        f"/api/v1/delivery-routes/{delivery_route['id']}/deactivate",
        headers=api_auth_headers,
    )

    with testing_session_local() as session:
        stored_route = session.get(DeliveryRoute, delivery_route["id"])
        assert stored_route is not None
        assert stored_route.is_active is False


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/delivery-routes", {"name": "Ruta Centro"}),
        ("GET", "/api/v1/delivery-routes", None),
        ("GET", "/api/v1/delivery-routes/1", None),
        ("PATCH", "/api/v1/delivery-routes/1", {"name": "Ruta Centro"}),
        ("PATCH", "/api/v1/delivery-routes/1/deactivate", None),
        ("PATCH", "/api/v1/delivery-routes/1/activate", None),
    ],
)
def test_delivery_route_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, str] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_delivery_route_migration_creates_table(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0006_create_delivery_routes.py"
    )
    spec = importlib.util.spec_from_file_location("migration_0006_routes", migration_path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[tuple[str, tuple[object, ...]]] = []

    def record_create_table(table_name: str, *elements: object) -> None:
        created_tables.append((table_name, elements))

    monkeypatch.setattr(migration.op, "create_table", record_create_table)

    migration.upgrade()

    assert migration.revision == "0006_routes"
    assert migration.down_revision == "0005_employees"
    assert len(migration.revision) <= 32
    assert [table_name for table_name, _ in created_tables] == ["delivery_routes"]
    column_names = {
        element.name
        for element in created_tables[0][1]
        if element.__class__.__name__ == "Column"
    }
    assert column_names == {
        "id",
        "code",
        "name",
        "description",
        "zone",
        "sector",
        "service_days",
        "reference_driver",
        "reference_vehicle",
        "expected_daily_cash",
        "is_active",
        "notes",
        "created_at",
        "updated_at",
    }


def _delivery_route_payload(**overrides):
    return {
        "code": None,
        "name": "Ruta Agua Activa",
        "expected_daily_cash": "0.00",
        **overrides,
    }


def _create_delivery_route(client, headers: dict[str, str], **overrides):
    response = client.post(
        "/api/v1/delivery-routes",
        headers=headers,
        json=_delivery_route_payload(**overrides),
    )
    assert response.status_code == 201
    return response.json()
