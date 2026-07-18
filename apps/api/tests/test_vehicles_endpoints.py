import importlib.util
from pathlib import Path

import pytest

from app.models.vehicle import Vehicle


def test_create_vehicle(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        json={
            "code": "CAMION-01",
            "name": "Camión 1",
            "plate": "ABC-1234",
            "vehicle_type": "truck",
            "brand": "Hino",
            "model": "Dutro",
            "year": 2018,
            "color": "Blanco",
            "fuel_type": "diesel",
            "capacity_reference": "120 bidones",
            "reference_driver": "Pedro Zambrano",
            "notes": "Vehículo principal de reparto",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["code"] == "CAMION-01"
    assert body["name"] == "Camión 1"
    assert body["plate"] == "ABC-1234"
    assert body["vehicle_type"] == "truck"
    assert body["brand"] == "Hino"
    assert body["model"] == "Dutro"
    assert body["year"] == 2018
    assert body["fuel_type"] == "diesel"
    assert body["capacity_reference"] == "120 bidones"
    assert body["reference_driver"] == "Pedro Zambrano"
    assert body["is_active"] is True
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_create_vehicle_requires_name(api_client, api_auth_headers) -> None:
    client, _ = api_client
    payload = _vehicle_payload()
    payload.pop("name")

    response = client.post(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_create_vehicle_rejects_blank_name(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        json=_vehicle_payload(name="   "),
    )

    assert response.status_code == 422


def test_create_vehicle_rejects_duplicate_code(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_vehicle(client, api_auth_headers, code="CAMION-01")

    response = client.post(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        json=_vehicle_payload(name="Otro camión", code="CAMION-01"),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "El codigo del vehiculo ya esta registrado."


def test_create_vehicle_rejects_duplicate_plate(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_vehicle(client, api_auth_headers, plate="ABC-1234")

    response = client.post(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        json=_vehicle_payload(name="Otro camión", plate="ABC-1234"),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "La placa del vehiculo ya esta registrada."


def test_create_vehicle_allows_blank_or_null_code(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    first = _create_vehicle(client, api_auth_headers, name="Camión A", code="   ")
    second = _create_vehicle(client, api_auth_headers, name="Camión B", code=None)

    assert first["code"] is None
    assert second["code"] is None


def test_create_vehicle_allows_blank_or_null_plate(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    first = _create_vehicle(client, api_auth_headers, name="Camión A", plate="   ")
    second = _create_vehicle(client, api_auth_headers, name="Camión B", plate=None)

    assert first["plate"] is None
    assert second["plate"] is None


@pytest.mark.parametrize("year", [-1, 1800, 2101])
def test_create_vehicle_rejects_unreasonable_year(
    api_client,
    api_auth_headers,
    year: int,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        json=_vehicle_payload(year=year),
    )

    assert response.status_code == 422


def test_list_vehicles(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_vehicle(client, api_auth_headers, name="Furgoneta 2")
    _create_vehicle(client, api_auth_headers, name="Camión 1")

    response = client.get("/api/v1/vehicles", headers=api_auth_headers)

    assert response.status_code == 200
    assert [vehicle["name"] for vehicle in response.json()] == ["Camión 1", "Furgoneta 2"]


@pytest.mark.parametrize(
    "search",
    ["Camión 1", "ABC-1234", "CAMION-01", "truck", "Hino", "Dutro"],
)
def test_list_vehicles_searches_expected_fields(
    api_client,
    api_auth_headers,
    search: str,
) -> None:
    client, _ = api_client
    _create_vehicle(
        client,
        api_auth_headers,
        code="CAMION-01",
        name="Camión 1",
        plate="ABC-1234",
        vehicle_type="truck",
        brand="Hino",
        model="Dutro",
    )
    _create_vehicle(
        client,
        api_auth_headers,
        code="MOTO-01",
        name="Moto 1",
        plate="XYZ-9876",
        vehicle_type="motorcycle",
        brand="Honda",
        model="CB1",
    )

    response = client.get(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        params={"search": search},
    )

    assert response.status_code == 200
    assert [vehicle["name"] for vehicle in response.json()] == ["Camión 1"]


def test_list_vehicles_filters_by_active_status(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    active = _create_vehicle(client, api_auth_headers, name="Vehículo activo")
    inactive = _create_vehicle(client, api_auth_headers, name="Vehículo inactivo")
    client.patch(
        f"/api/v1/vehicles/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.get(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        params={"is_active": "true"},
    )

    assert response.status_code == 200
    assert [vehicle["id"] for vehicle in response.json()] == [active["id"]]


def test_list_vehicles_filters_by_vehicle_type(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_vehicle(client, api_auth_headers, name="Camión", vehicle_type="truck")
    _create_vehicle(client, api_auth_headers, name="Moto", vehicle_type="motorcycle")

    response = client.get(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        params={"vehicle_type": "truck"},
    )

    assert response.status_code == 200
    assert [vehicle["name"] for vehicle in response.json()] == ["Camión"]


def test_list_vehicles_filters_by_fuel_type(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_vehicle(client, api_auth_headers, name="Diésel", fuel_type="diesel")
    _create_vehicle(client, api_auth_headers, name="Gasolina", fuel_type="gasoline")

    response = client.get(
        "/api/v1/vehicles",
        headers=api_auth_headers,
        params={"fuel_type": "diesel"},
    )

    assert response.status_code == 200
    assert [vehicle["name"] for vehicle in response.json()] == ["Diésel"]


def test_get_vehicle_detail(api_client, api_auth_headers) -> None:
    client, _ = api_client
    vehicle = _create_vehicle(client, api_auth_headers)

    response = client.get(
        f"/api/v1/vehicles/{vehicle['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == vehicle


def test_get_vehicle_detail_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get("/api/v1/vehicles/999", headers=api_auth_headers)

    assert response.status_code == 404


def test_update_vehicle(api_client, api_auth_headers) -> None:
    client, _ = api_client
    vehicle = _create_vehicle(client, api_auth_headers, name="Vehículo original")

    response = client.patch(
        f"/api/v1/vehicles/{vehicle['id']}",
        headers=api_auth_headers,
        json={
            "name": "Camión actualizado",
            "brand": "Hino",
            "model": "Dutro",
            "year": 2020,
            "fuel_type": "diesel",
            "capacity_reference": "140 bidones",
            "notes": "Datos revisados",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Camión actualizado"
    assert body["brand"] == "Hino"
    assert body["model"] == "Dutro"
    assert body["year"] == 2020
    assert body["fuel_type"] == "diesel"
    assert body["capacity_reference"] == "140 bidones"
    assert body["notes"] == "Datos revisados"


def test_deactivate_vehicle(api_client, api_auth_headers) -> None:
    client, _ = api_client
    vehicle = _create_vehicle(client, api_auth_headers)

    response = client.patch(
        f"/api/v1/vehicles/{vehicle['id']}/deactivate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_reactivate_vehicle(api_client, api_auth_headers) -> None:
    client, _ = api_client
    vehicle = _create_vehicle(client, api_auth_headers)
    client.patch(
        f"/api/v1/vehicles/{vehicle['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.patch(
        f"/api/v1/vehicles/{vehicle['id']}/activate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_deactivate_vehicle_does_not_delete_record(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    vehicle = _create_vehicle(client, api_auth_headers)

    client.patch(
        f"/api/v1/vehicles/{vehicle['id']}/deactivate",
        headers=api_auth_headers,
    )

    with testing_session_local() as session:
        stored_vehicle = session.get(Vehicle, vehicle["id"])
        assert stored_vehicle is not None
        assert stored_vehicle.is_active is False


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/vehicles", {"name": "Camión 1"}),
        ("GET", "/api/v1/vehicles", None),
        ("GET", "/api/v1/vehicles/1", None),
        ("PATCH", "/api/v1/vehicles/1", {"name": "Camión 1"}),
        ("PATCH", "/api/v1/vehicles/1/deactivate", None),
        ("PATCH", "/api/v1/vehicles/1/activate", None),
    ],
)
def test_vehicle_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, str] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_vehicle_migration_creates_vehicles_table(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0007_create_vehicles.py"
    )
    spec = importlib.util.spec_from_file_location("migration_0007_vehicles", migration_path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[tuple[str, tuple[object, ...]]] = []

    def record_create_table(table_name: str, *elements: object) -> None:
        created_tables.append((table_name, elements))

    monkeypatch.setattr(migration.op, "create_table", record_create_table)

    migration.upgrade()

    assert migration.revision == "0007_vehicles"
    assert migration.down_revision == "0006_routes"
    assert len(migration.revision) <= 32
    assert [table_name for table_name, _ in created_tables] == ["vehicles"]
    column_names = {
        element.name
        for element in created_tables[0][1]
        if element.__class__.__name__ == "Column"
    }
    assert column_names == {
        "id",
        "code",
        "name",
        "plate",
        "vehicle_type",
        "brand",
        "model",
        "year",
        "color",
        "fuel_type",
        "capacity_reference",
        "reference_driver",
        "is_active",
        "notes",
        "created_at",
        "updated_at",
    }


def _vehicle_payload(**overrides):
    return {
        "code": None,
        "name": "Vehículo Agua Activa",
        "plate": None,
        "vehicle_type": "other",
        "fuel_type": "other",
        **overrides,
    }


def _create_vehicle(client, headers: dict[str, str], **overrides):
    response = client.post(
        "/api/v1/vehicles",
        headers=headers,
        json=_vehicle_payload(**overrides),
    )
    assert response.status_code == 201
    return response.json()
