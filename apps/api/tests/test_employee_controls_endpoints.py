import importlib.util
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.models.cash_session import CashSession
from app.models.employee_advance import EmployeeAdvance
from app.models.employee_attendance import EmployeeAttendance
from app.models.employee_loan import EmployeeLoan
from app.models.employee_loan_payment import EmployeeLoanPayment
from app.models.operating_expense import OperatingExpense


def test_create_list_get_and_update_attendance(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)

    created = client.post(
        "/api/v1/employees/attendance",
        headers=api_auth_headers,
        json=_attendance_payload(employee["id"]),
    )

    assert created.status_code == 201
    body = created.json()
    assert body["employee_id"] == employee["id"]
    assert body["employee_name"] == "Pedro Zambrano"
    assert body["attendance_date"] == "2026-07-18"
    assert body["status"] == "present"
    assert body["check_in_time"] == "08:00:00"
    assert body["check_out_time"] == "17:00:00"
    assert body["hours_worked"] == "8.00"

    detail = client.get(
        f"/api/v1/employees/attendance/{body['id']}",
        headers=api_auth_headers,
    )
    assert detail.status_code == 200
    assert detail.json()["id"] == body["id"]

    listed = client.get(
        "/api/v1/employees/attendance",
        headers=api_auth_headers,
        params={
            "date_from": "2026-07-18",
            "date_to": "2026-07-18",
            "employee_id": employee["id"],
            "status": "present",
        },
    )
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [body["id"]]

    updated = client.patch(
        f"/api/v1/employees/attendance/{body['id']}",
        headers=api_auth_headers,
        json={
            "status": "late",
            "check_in_time": "08:20",
            "hours_worked": "7.50",
            "notes": "Ingreso tardio",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "late"
    assert updated.json()["hours_worked"] == "7.50"
    assert updated.json()["notes"] == "Ingreso tardio"


def test_attendance_rejects_duplicate_employee_date(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    payload = _attendance_payload(employee["id"])
    assert client.post(
        "/api/v1/employees/attendance",
        headers=api_auth_headers,
        json=payload,
    ).status_code == 201

    duplicate = client.post(
        "/api/v1/employees/attendance",
        headers=api_auth_headers,
        json=payload,
    )

    assert duplicate.status_code == 409
    assert "Ya existe asistencia" in duplicate.json()["detail"]


@pytest.mark.parametrize(
    ("payload_override", "expected_status"),
    [
        ({"employee_id": 999}, 404),
        ({"status": "remote"}, 422),
        ({"hours_worked": "-0.01"}, 422),
    ],
)
def test_attendance_rejects_invalid_data(
    api_client,
    api_auth_headers,
    payload_override: dict[str, object],
    expected_status: int,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    payload = _attendance_payload(employee["id"])
    payload.update(payload_override)

    response = client.post(
        "/api/v1/employees/attendance",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == expected_status


def test_controls_reject_inactive_employee(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    client.patch(
        f"/api/v1/employees/{employee['id']}/deactivate",
        headers=api_auth_headers,
    )

    responses = [
        client.post(
            "/api/v1/employees/attendance",
            headers=api_auth_headers,
            json=_attendance_payload(employee["id"]),
        ),
        client.post(
            "/api/v1/employees/advances",
            headers=api_auth_headers,
            json=_advance_payload(employee["id"]),
        ),
        client.post(
            "/api/v1/employees/loans",
            headers=api_auth_headers,
            json=_loan_payload(employee["id"]),
        ),
    ]

    assert [response.status_code for response in responses] == [400, 400, 400]
    assert all(
        response.json()["detail"] == "El empleado esta inactivo."
        for response in responses
    )


def test_create_list_get_and_void_advance(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)
    counts_before = _financial_counts(testing_session_local)

    created = client.post(
        "/api/v1/employees/advances",
        headers=api_auth_headers,
        json=_advance_payload(employee["id"]),
    )

    assert created.status_code == 201
    body = created.json()
    assert body["advance_number"].startswith("ADV-20260718-")
    assert body["employee_name"] == "Pedro Zambrano"
    assert body["amount"] == "20.00"
    assert body["reason"] == "Anticipo de sueldo"
    assert body["status"] == "active"

    detail = client.get(
        f"/api/v1/employees/advances/{body['id']}",
        headers=api_auth_headers,
    )
    assert detail.status_code == 200
    listed = client.get(
        "/api/v1/employees/advances",
        headers=api_auth_headers,
        params={"employee_id": employee["id"], "status": "active"},
    )
    assert [item["id"] for item in listed.json()] == [body["id"]]

    voided = client.post(
        f"/api/v1/employees/advances/{body['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Registro duplicado"},
    )
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    assert voided.json()["void_reason"] == "Registro duplicado"
    assert voided.json()["voided_at"] is not None
    assert _financial_counts(testing_session_local) == counts_before

    repeated = client.post(
        f"/api/v1/employees/advances/{body['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Otro motivo"},
    )
    assert repeated.status_code == 409


@pytest.mark.parametrize(
    "payload_override",
    [
        {"amount": "0"},
        {"amount": "-1.00"},
        {"reason": "   "},
    ],
)
def test_advance_rejects_invalid_amount_or_reason(
    api_client,
    api_auth_headers,
    payload_override: dict[str, str],
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    payload = _advance_payload(employee["id"])
    payload.update(payload_override)

    response = client.post(
        "/api/v1/employees/advances",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_loan_payment_lifecycle_and_financial_isolation(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)
    counts_before = _financial_counts(testing_session_local)

    loan = _create_loan(client, api_auth_headers, employee["id"])
    assert loan["loan_number"].startswith("LOAN-20260718-")
    assert loan["principal_amount"] == "100.00"
    assert loan["paid_amount"] == "0.00"
    assert loan["balance_amount"] == "100.00"
    assert loan["status"] == "active"

    partial = _create_payment(
        client,
        api_auth_headers,
        loan["id"],
        amount="25.00",
        payment_date="2026-07-20",
    )
    assert partial["payment_number"].startswith("ELP-20260720-")
    assert partial["employee_id"] == employee["id"]
    assert partial["loan_number"] == loan["loan_number"]

    loan_after_partial = client.get(
        f"/api/v1/employees/loans/{loan['id']}",
        headers=api_auth_headers,
    ).json()
    assert loan_after_partial["paid_amount"] == "25.00"
    assert loan_after_partial["balance_amount"] == "75.00"
    assert loan_after_partial["status"] == "active"

    total = _create_payment(
        client,
        api_auth_headers,
        loan["id"],
        amount="75.00",
        payment_date="2026-07-21",
    )
    loan_paid = client.get(
        f"/api/v1/employees/loans/{loan['id']}",
        headers=api_auth_headers,
    ).json()
    assert loan_paid["paid_amount"] == "100.00"
    assert loan_paid["balance_amount"] == "0.00"
    assert loan_paid["status"] == "paid"

    rejected_paid = client.post(
        f"/api/v1/employees/loans/{loan['id']}/payments",
        headers=api_auth_headers,
        json={"payment_date": "2026-07-22", "amount": "1.00"},
    )
    assert rejected_paid.status_code == 409

    voided = client.post(
        f"/api/v1/employees/loan-payments/{total['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Pago registrado por error"},
    )
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    restored_loan = client.get(
        f"/api/v1/employees/loans/{loan['id']}",
        headers=api_auth_headers,
    ).json()
    assert restored_loan["paid_amount"] == "25.00"
    assert restored_loan["balance_amount"] == "75.00"
    assert restored_loan["status"] == "active"

    repeated = client.post(
        f"/api/v1/employees/loan-payments/{total['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Segundo intento"},
    )
    assert repeated.status_code == 409
    assert _financial_counts(testing_session_local) == counts_before


def test_loan_rejects_invalid_principal_and_overpayment(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)

    invalid_loan = client.post(
        "/api/v1/employees/loans",
        headers=api_auth_headers,
        json=_loan_payload(employee["id"], principal_amount="0"),
    )
    assert invalid_loan.status_code == 422

    missing_reason = client.post(
        "/api/v1/employees/loans",
        headers=api_auth_headers,
        json=_loan_payload(employee["id"], reason=" "),
    )
    assert missing_reason.status_code == 422

    loan = _create_loan(client, api_auth_headers, employee["id"])
    overpayment = client.post(
        f"/api/v1/employees/loans/{loan['id']}/payments",
        headers=api_auth_headers,
        json={"payment_date": "2026-07-20", "amount": "100.01"},
    )
    assert overpayment.status_code == 400
    assert "saldo pendiente" in overpayment.json()["detail"]


def test_loan_void_rules(api_client, api_auth_headers) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    loan_with_payment = _create_loan(client, api_auth_headers, employee["id"])
    _create_payment(
        client,
        api_auth_headers,
        loan_with_payment["id"],
        amount="10.00",
    )

    rejected = client.post(
        f"/api/v1/employees/loans/{loan_with_payment['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    )
    assert rejected.status_code == 409

    loan_without_payment = _create_loan(
        client,
        api_auth_headers,
        employee["id"],
        loan_date="2026-07-19",
    )
    voided = client.post(
        f"/api/v1/employees/loans/{loan_without_payment['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Prestamo registrado por error"},
    )
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"

    rejected_payment = client.post(
        f"/api/v1/employees/loans/{loan_without_payment['id']}/payments",
        headers=api_auth_headers,
        json={"payment_date": "2026-07-20", "amount": "1.00"},
    )
    assert rejected_payment.status_code == 409


def test_account_summary_excludes_voided_records(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    client.post(
        "/api/v1/employees/attendance",
        headers=api_auth_headers,
        json=_attendance_payload(employee["id"]),
    )
    active_advance = _create_advance(client, api_auth_headers, employee["id"])
    voided_advance = _create_advance(
        client,
        api_auth_headers,
        employee["id"],
        advance_date="2026-07-19",
        amount="10.00",
    )
    client.post(
        f"/api/v1/employees/advances/{voided_advance['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    )
    loan = _create_loan(client, api_auth_headers, employee["id"])
    _create_payment(
        client,
        api_auth_headers,
        loan["id"],
        amount="25.00",
    )
    voided_loan = _create_loan(
        client,
        api_auth_headers,
        employee["id"],
        loan_date="2026-07-19",
        principal_amount="40.00",
    )
    client.post(
        f"/api/v1/employees/loans/{voided_loan['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    )

    response = client.get(
        f"/api/v1/employees/{employee['id']}/account-summary",
        headers=api_auth_headers,
        params={"date_from": "2026-07-18", "date_to": "2026-07-20"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == employee["id"]
    assert body["advances_total_active"] == active_advance["amount"]
    assert body["loans_principal_total"] == "100.00"
    assert body["loans_paid_total"] == "25.00"
    assert body["loans_balance_total"] == "75.00"
    assert body["active_loans_count"] == 1
    assert body["paid_loans_count"] == 0
    assert body["attendance_count_period"] == 1
    assert len(body["latest_advances"]) == 2
    assert len(body["latest_loans"]) == 2
    assert len(body["latest_loan_payments"]) == 1


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/employees/attendance", {}),
        ("GET", "/api/v1/employees/attendance", None),
        ("POST", "/api/v1/employees/advances", {}),
        ("GET", "/api/v1/employees/advances", None),
        ("POST", "/api/v1/employees/loans", {}),
        ("GET", "/api/v1/employees/loans", None),
        ("GET", "/api/v1/employees/loan-payments", None),
        ("GET", "/api/v1/employees/1/account-summary", None),
    ],
)
def test_employee_control_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_employee_controls_migration_defines_tables_checks_and_indexes(
    monkeypatch,
) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0022_employee_controls.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0022_employee_controls",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[str] = []
    created_indexes: list[tuple[str, str]] = []

    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *elements: created_tables.append(table_name),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda index_name, table_name, columns: created_indexes.append(
            (index_name, table_name),
        ),
    )

    migration.upgrade()

    assert migration.revision == "0022_employee_controls"
    assert migration.down_revision == "0021_op_expenses"
    assert len(migration.revision) <= 32
    assert created_tables == [
        "employee_attendance",
        "employee_advances",
        "employee_loans",
        "employee_loan_payments",
    ]
    assert len(created_indexes) == 16


def test_employee_controls_do_not_create_fake_data(
    api_client,
) -> None:
    _, testing_session_local = api_client
    with testing_session_local() as session:
        assert session.scalar(select(func.count()).select_from(EmployeeAttendance)) == 0
        assert session.scalar(select(func.count()).select_from(EmployeeAdvance)) == 0
        assert session.scalar(select(func.count()).select_from(EmployeeLoan)) == 0
        assert (
            session.scalar(select(func.count()).select_from(EmployeeLoanPayment))
            == 0
        )


def _create_employee(client, headers) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees",
        headers=headers,
        json={
            "first_name": "Pedro",
            "last_name": "Zambrano",
            "employee_type": "driver",
            "base_salary": "500.00",
            "payment_frequency": "monthly",
        },
    )
    assert response.status_code == 201
    return response.json()


def _attendance_payload(employee_id: int) -> dict[str, object]:
    return {
        "employee_id": employee_id,
        "attendance_date": "2026-07-18",
        "status": "present",
        "check_in_time": "08:00",
        "check_out_time": "17:00",
        "hours_worked": "8",
        "notes": "Jornada normal",
    }


def _advance_payload(
    employee_id: int,
    *,
    advance_date: str = "2026-07-18",
    amount: str = "20.00",
) -> dict[str, object]:
    return {
        "employee_id": employee_id,
        "advance_date": advance_date,
        "amount": amount,
        "reason": "Anticipo de sueldo",
        "notes": "Solicitado por el empleado",
    }


def _create_advance(
    client,
    headers,
    employee_id: int,
    *,
    advance_date: str = "2026-07-18",
    amount: str = "20.00",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees/advances",
        headers=headers,
        json=_advance_payload(
            employee_id,
            advance_date=advance_date,
            amount=amount,
        ),
    )
    assert response.status_code == 201
    return response.json()


def _loan_payload(
    employee_id: int,
    *,
    loan_date: str = "2026-07-18",
    principal_amount: str = "100.00",
    reason: str = "Prestamo interno",
) -> dict[str, object]:
    return {
        "employee_id": employee_id,
        "loan_date": loan_date,
        "principal_amount": principal_amount,
        "reason": reason,
        "notes": "A descontar en pagos futuros",
    }


def _create_loan(
    client,
    headers,
    employee_id: int,
    *,
    loan_date: str = "2026-07-18",
    principal_amount: str = "100.00",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees/loans",
        headers=headers,
        json=_loan_payload(
            employee_id,
            loan_date=loan_date,
            principal_amount=principal_amount,
        ),
    )
    assert response.status_code == 201
    return response.json()


def _create_payment(
    client,
    headers,
    loan_id: int,
    *,
    amount: str,
    payment_date: str = "2026-07-20",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/employees/loans/{loan_id}/payments",
        headers=headers,
        json={
            "payment_date": payment_date,
            "amount": amount,
            "notes": "Abono controlado",
        },
    )
    assert response.status_code == 201
    return response.json()


def _financial_counts(testing_session_local) -> tuple[int, int]:
    with testing_session_local() as session:
        return (
            session.scalar(select(func.count()).select_from(CashSession)) or 0,
            session.scalar(select(func.count()).select_from(OperatingExpense))
            or 0,
        )
