import importlib.util
from pathlib import Path

import pytest

from app.models.employee import Employee


def test_create_employee(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/employees",
        headers=api_auth_headers,
        json={
            "first_name": "Pedro",
            "last_name": "Zambrano",
            "identification": "1300000000",
            "primary_phone": "0999999999",
            "secondary_phone": "052000000",
            "address": "Manta",
            "job_position": "Chofer",
            "employee_type": "driver",
            "base_salary": "500.00",
            "payment_frequency": "monthly",
            "hire_date": "2026-07-01",
            "notes": "Chofer de ruta",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["first_name"] == "Pedro"
    assert body["last_name"] == "Zambrano"
    assert body["identification"] == "1300000000"
    assert body["employee_type"] == "driver"
    assert body["base_salary"] == "500.00"
    assert body["payment_frequency"] == "monthly"
    assert body["hire_date"] == "2026-07-01"
    assert body["termination_date"] is None
    assert body["is_active"] is True
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


@pytest.mark.parametrize("missing_field", ["first_name", "last_name"])
def test_create_employee_requires_names(
    api_client,
    api_auth_headers,
    missing_field: str,
) -> None:
    client, _ = api_client
    payload = _employee_payload()
    payload.pop(missing_field)

    response = client.post(
        "/api/v1/employees",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize("field_name", ["first_name", "last_name"])
def test_create_employee_rejects_blank_names(
    api_client,
    api_auth_headers,
    field_name: str,
) -> None:
    client, _ = api_client
    payload = _employee_payload(**{field_name: "   "})

    response = client.post(
        "/api/v1/employees",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_create_employee_rejects_negative_base_salary(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/employees",
        headers=api_auth_headers,
        json=_employee_payload(base_salary="-0.01"),
    )

    assert response.status_code == 422


def test_create_employee_rejects_duplicate_identification(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_employee(client, api_auth_headers, identification="1300000000")

    response = client.post(
        "/api/v1/employees",
        headers=api_auth_headers,
        json=_employee_payload(
            first_name="Maria",
            last_name="Lopez",
            identification="1300000000",
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "La identificacion ya esta registrada."


def test_create_employee_allows_blank_or_null_identification(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    first = _create_employee(
        client,
        api_auth_headers,
        first_name="Ana",
        identification="   ",
    )
    second = _create_employee(
        client,
        api_auth_headers,
        first_name="Luis",
        identification=None,
    )

    assert first["identification"] is None
    assert second["identification"] is None


def test_list_employees(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_employee(client, api_auth_headers, first_name="Pedro", last_name="Zambrano")
    _create_employee(client, api_auth_headers, first_name="Ana", last_name="Alvarez")

    response = client.get("/api/v1/employees", headers=api_auth_headers)

    assert response.status_code == 200
    assert [employee["first_name"] for employee in response.json()] == ["Ana", "Pedro"]


@pytest.mark.parametrize(
    "search",
    [
        "Pedro",
        "Pedro Zambrano",
        "1300000000",
        "0999999999",
        "Chofer",
        "driver",
    ],
)
def test_list_employees_searches_expected_fields(
    api_client,
    api_auth_headers,
    search: str,
) -> None:
    client, _ = api_client
    _create_employee(
        client,
        api_auth_headers,
        first_name="Pedro",
        last_name="Zambrano",
        identification="1300000000",
        primary_phone="0999999999",
        job_position="Chofer",
        employee_type="driver",
    )
    _create_employee(
        client,
        api_auth_headers,
        first_name="Ana",
        last_name="Lopez",
        identification="1300000001",
        primary_phone="0988888888",
        job_position="Oficina",
        employee_type="office",
    )

    response = client.get(
        "/api/v1/employees",
        headers=api_auth_headers,
        params={"search": search},
    )

    assert response.status_code == 200
    assert [employee["first_name"] for employee in response.json()] == ["Pedro"]


def test_list_employees_filters_by_active_status(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    active = _create_employee(client, api_auth_headers, first_name="Activo")
    inactive = _create_employee(client, api_auth_headers, first_name="Inactivo")
    client.patch(
        f"/api/v1/employees/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.get(
        "/api/v1/employees",
        headers=api_auth_headers,
        params={"is_active": "true"},
    )

    assert response.status_code == 200
    assert [employee["id"] for employee in response.json()] == [active["id"]]


def test_list_employees_filters_by_employee_type(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_employee(client, api_auth_headers, first_name="Pedro", employee_type="driver")
    _create_employee(client, api_auth_headers, first_name="Ana", employee_type="office")

    response = client.get(
        "/api/v1/employees",
        headers=api_auth_headers,
        params={"employee_type": "driver"},
    )

    assert response.status_code == 200
    assert [employee["first_name"] for employee in response.json()] == ["Pedro"]


def test_list_employees_filters_by_job_position(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_employee(client, api_auth_headers, first_name="Pedro", job_position="Chofer")
    _create_employee(client, api_auth_headers, first_name="Ana", job_position="Oficina")

    response = client.get(
        "/api/v1/employees",
        headers=api_auth_headers,
        params={"job_position": "chofer"},
    )

    assert response.status_code == 200
    assert [employee["first_name"] for employee in response.json()] == ["Pedro"]


def test_get_employee_detail(api_client, api_auth_headers) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)

    response = client.get(
        f"/api/v1/employees/{employee['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == employee


def test_get_employee_detail_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get("/api/v1/employees/999", headers=api_auth_headers)

    assert response.status_code == 404


def test_update_employee(api_client, api_auth_headers) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)

    response = client.patch(
        f"/api/v1/employees/{employee['id']}",
        headers=api_auth_headers,
        json={
            "first_name": "Pedro Luis",
            "job_position": "Chofer principal",
            "base_salary": "550.25",
            "payment_frequency": "biweekly",
            "hire_date": "2026-06-15",
            "notes": "Datos actualizados",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Pedro Luis"
    assert body["job_position"] == "Chofer principal"
    assert body["base_salary"] == "550.25"
    assert body["payment_frequency"] == "biweekly"
    assert body["hire_date"] == "2026-06-15"
    assert body["notes"] == "Datos actualizados"


def test_deactivate_employee_can_store_termination_date(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)

    response = client.patch(
        f"/api/v1/employees/{employee['id']}/deactivate",
        headers=api_auth_headers,
        json={"termination_date": "2026-07-18"},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert response.json()["termination_date"] == "2026-07-18"


def test_reactivate_employee_clears_termination_date(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    client.patch(
        f"/api/v1/employees/{employee['id']}/deactivate",
        headers=api_auth_headers,
        json={"termination_date": "2026-07-18"},
    )

    response = client.patch(
        f"/api/v1/employees/{employee['id']}/activate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True
    assert response.json()["termination_date"] is None


def test_deactivate_employee_does_not_delete_record(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)

    client.patch(
        f"/api/v1/employees/{employee['id']}/deactivate",
        headers=api_auth_headers,
    )

    with testing_session_local() as session:
        stored_employee = session.get(Employee, employee["id"])
        assert stored_employee is not None
        assert stored_employee.is_active is False


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        (
            "POST",
            "/api/v1/employees",
            {"first_name": "Pedro", "last_name": "Zambrano"},
        ),
        ("GET", "/api/v1/employees", None),
        ("GET", "/api/v1/employees/1", None),
        ("PATCH", "/api/v1/employees/1", {"job_position": "Chofer"}),
        ("PATCH", "/api/v1/employees/1/deactivate", None),
        ("PATCH", "/api/v1/employees/1/activate", None),
    ],
)
def test_employee_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, str] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_employee_migration_creates_employees_table(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0005_create_employees.py"
    )
    spec = importlib.util.spec_from_file_location("migration_0005_employees", migration_path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[tuple[str, tuple[object, ...]]] = []

    def record_create_table(table_name: str, *elements: object) -> None:
        created_tables.append((table_name, elements))

    monkeypatch.setattr(migration.op, "create_table", record_create_table)

    migration.upgrade()

    assert migration.revision == "0005_employees"
    assert migration.down_revision == "0004_products"
    assert len(migration.revision) <= 32
    assert [table_name for table_name, _ in created_tables] == ["employees"]
    column_names = {
        element.name
        for element in created_tables[0][1]
        if element.__class__.__name__ == "Column"
    }
    assert column_names == {
        "id",
        "first_name",
        "last_name",
        "identification",
        "primary_phone",
        "secondary_phone",
        "address",
        "job_position",
        "employee_type",
        "base_salary",
        "payment_frequency",
        "hire_date",
        "termination_date",
        "is_active",
        "notes",
        "created_at",
        "updated_at",
    }


def _employee_payload(**overrides):
    return {
        "first_name": "Pedro",
        "last_name": "Zambrano",
        "identification": None,
        "employee_type": "other",
        "base_salary": "0.00",
        "payment_frequency": "monthly",
        **overrides,
    }


def _create_employee(client, headers: dict[str, str], **overrides):
    response = client.post(
        "/api/v1/employees",
        headers=headers,
        json=_employee_payload(**overrides),
    )
    assert response.status_code == 201
    return response.json()
