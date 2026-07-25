import importlib.util
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.models.cash_session import CashSession
from app.models.employee_advance import EmployeeAdvance
from app.models.employee_loan import EmployeeLoan
from app.models.employee_loan_payment import EmployeeLoanPayment
from app.models.operating_expense import OperatingExpense
from app.models.payroll_item import PayrollItem
from app.models.payroll_item_advance_deduction import (
    PayrollItemAdvanceDeduction,
)
from app.models.payroll_item_loan_deduction import PayrollItemLoanDeduction
from app.models.payroll_run import PayrollRun


def test_preview_calculates_payroll_without_persisting_or_mutating_sources(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    _create_attendance(
        client,
        api_auth_headers,
        employee["id"],
        "2026-07-02",
        "present",
        "8.00",
    )
    _create_attendance(
        client,
        api_auth_headers,
        employee["id"],
        "2026-07-03",
        "late",
        "7.50",
    )
    _create_attendance(
        client,
        api_auth_headers,
        employee["id"],
        "2026-07-04",
        "absent",
        None,
    )
    counts_before = _protected_counts(testing_session_local)

    response = client.post(
        "/api/v1/payroll/runs/preview",
        headers=api_auth_headers,
        json=_payroll_payload(
            employee["id"],
            advance_id=advance["id"],
            loan_id=loan["id"],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employees_count"] == 1
    assert body["gross_total"] == "530.00"
    assert body["bonuses_total"] == "20.00"
    assert body["advances_deducted_total"] == "20.00"
    assert body["loan_deductions_total"] == "25.00"
    assert body["other_deductions_total"] == "5.00"
    assert body["total_deductions"] == "50.00"
    assert body["net_pay_total"] == "480.00"
    item = body["items"][0]
    assert item["base_salary_snapshot"] == "500.00"
    assert item["base_salary_amount"] == "500.00"
    assert item["other_income_amount"] == "10.00"
    assert item["attendance_days"] == 2
    assert item["late_days"] == 1
    assert item["absent_days"] == 1
    assert item["hours_worked"] == "15.50"
    assert item["net_pay_amount"] == "480.00"
    assert item["advance_deductions"][0]["amount_deducted"] == "20.00"
    assert item["loan_deductions"][0]["amount_deducted"] == "25.00"
    assert _payroll_counts(testing_session_local) == (0, 0, 0, 0)
    assert _protected_counts(testing_session_local) == counts_before
    _assert_sources_unchanged(
        testing_session_local,
        advance["id"],
        loan["id"],
    )


def test_create_multi_employee_payroll_saves_snapshots_totals_and_detail(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    first = _create_employee(client, api_auth_headers)
    second = _create_employee(
        client,
        api_auth_headers,
        first_name="Ana",
        last_name="Vera",
        identification="0912345678",
        base_salary="400.00",
        job_position="Produccion",
    )
    advance = _create_advance(client, api_auth_headers, first["id"])
    loan = _create_loan(client, api_auth_headers, first["id"])
    payload = _payroll_payload(
        first["id"],
        advance_id=advance["id"],
        loan_id=loan["id"],
        include_payroll_date=True,
    )
    payload["employee_ids"] = [first["id"], second["id"]]

    response = client.post(
        "/api/v1/payroll/runs",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["payroll_number"].startswith("PAY-20260731-")
    assert body["status"] == "active"
    assert body["employees_count"] == 2
    assert body["gross_total"] == "930.00"
    assert body["net_pay_total"] == "880.00"
    assert len(body["items"]) == 2
    first_item = next(
        item for item in body["items"] if item["employee_id"] == first["id"]
    )
    second_item = next(
        item for item in body["items"] if item["employee_id"] == second["id"]
    )
    assert first_item["employee_name_snapshot"] == "Pedro Zambrano"
    assert first_item["employee_identification_snapshot"] == "1100000001"
    assert first_item["job_position_snapshot"] == "Chofer"
    assert first_item["payment_frequency_snapshot"] == "monthly"
    assert len(first_item["advance_deductions"]) == 1
    assert len(first_item["loan_deductions"]) == 1
    assert second_item["base_salary_amount"] == "400.00"
    assert second_item["net_pay_amount"] == "400.00"
    assert _payroll_counts(testing_session_local) == (1, 2, 1, 1)

    detail = client.get(
        f"/api/v1/payroll/runs/{body['id']}",
        headers=api_auth_headers,
    )
    assert detail.status_code == 200
    assert detail.json() == body

    list_filters = (
        {"date_from": "2026-07-31", "date_to": "2026-07-31"},
        {"status": "active"},
        {"employee_id": second["id"]},
        {"search": "Pedro"},
        {"search": body["payroll_number"]},
    )
    for filters in list_filters:
        listed = client.get(
            "/api/v1/payroll/runs",
            headers=api_auth_headers,
            params=filters,
        )
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()] == [body["id"]]
    _assert_sources_unchanged(
        testing_session_local,
        advance["id"],
        loan["id"],
    )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "employee_ids": [],
            "items": [],
        },
        {
            "period_start": "2026-07-31",
            "period_end": "2026-07-01",
            "employee_ids": [1],
        },
        {
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "employee_ids": [1, 1],
        },
        {
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "items": [{"employee_id": 1}, {"employee_id": 1}],
        },
        {
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "items": [{"employee_id": 1, "bonus_amount": "-0.01"}],
        },
        {
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "items": [{"employee_id": 1, "other_income_amount": "-0.01"}],
        },
        {
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "items": [{"employee_id": 1, "other_deductions_amount": "-0.01"}],
        },
    ],
)
def test_preview_rejects_invalid_request_shape(
    api_client,
    api_auth_headers,
    payload,
) -> None:
    client, _ = api_client
    response = client.post(
        "/api/v1/payroll/runs/preview",
        headers=api_auth_headers,
        json=payload,
    )
    assert response.status_code == 422


def test_payroll_rejects_missing_inactive_and_negative_net_employee(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    missing = client.post(
        "/api/v1/payroll/runs/preview",
        headers=api_auth_headers,
        json=_payroll_payload(999),
    )
    assert missing.status_code == 404

    employee = _create_employee(client, api_auth_headers)
    client.patch(
        f"/api/v1/employees/{employee['id']}/deactivate",
        headers=api_auth_headers,
    )
    inactive = client.post(
        "/api/v1/payroll/runs/preview",
        headers=api_auth_headers,
        json=_payroll_payload(employee["id"]),
    )
    assert inactive.status_code == 400

    low_salary = _create_employee(
        client,
        api_auth_headers,
        first_name="Luis",
        last_name="Paz",
        identification="1100000002",
        base_salary="10.00",
    )
    negative = client.post(
        "/api/v1/payroll/runs/preview",
        headers=api_auth_headers,
        json=_payroll_payload(low_salary["id"], other_deductions="40.01"),
    )
    assert negative.status_code == 400
    assert "no puede ser negativo" in negative.json()["detail"]


def test_payroll_validates_advances(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    other = _create_employee(
        client,
        api_auth_headers,
        first_name="Ana",
        last_name="Vera",
        identification="1100000002",
    )

    missing = _preview_with_advance(
        client,
        api_auth_headers,
        employee["id"],
        999,
    )
    assert missing.status_code == 404

    other_advance = _create_advance(client, api_auth_headers, other["id"])
    wrong_employee = _preview_with_advance(
        client,
        api_auth_headers,
        employee["id"],
        other_advance["id"],
    )
    assert wrong_employee.status_code == 400

    voided = _create_advance(
        client,
        api_auth_headers,
        employee["id"],
        advance_date="2026-07-19",
    )
    client.post(
        f"/api/v1/employees/advances/{voided['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    )
    rejected_voided = _preview_with_advance(
        client,
        api_auth_headers,
        employee["id"],
        voided["id"],
    )
    assert rejected_voided.status_code == 409


def test_payroll_validates_loans(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    other = _create_employee(
        client,
        api_auth_headers,
        first_name="Ana",
        last_name="Vera",
        identification="1100000002",
    )
    missing = _preview_with_loan(
        client,
        api_auth_headers,
        employee["id"],
        999,
        "1.00",
    )
    assert missing.status_code == 404

    other_loan = _create_loan(client, api_auth_headers, other["id"])
    wrong_employee = _preview_with_loan(
        client,
        api_auth_headers,
        employee["id"],
        other_loan["id"],
        "1.00",
    )
    assert wrong_employee.status_code == 400

    loan = _create_loan(client, api_auth_headers, employee["id"])
    over_balance = _preview_with_loan(
        client,
        api_auth_headers,
        employee["id"],
        loan["id"],
        "100.01",
    )
    assert over_balance.status_code == 400

    paid = _create_loan(
        client,
        api_auth_headers,
        employee["id"],
        loan_date="2026-07-19",
        principal_amount="10.00",
    )
    payment = client.post(
        f"/api/v1/employees/loans/{paid['id']}/payments",
        headers=api_auth_headers,
        json={"payment_date": "2026-07-20", "amount": "10.00"},
    )
    assert payment.status_code == 201
    rejected_paid = _preview_with_loan(
        client,
        api_auth_headers,
        employee["id"],
        paid["id"],
        "1.00",
    )
    assert rejected_paid.status_code == 409

    voided = _create_loan(
        client,
        api_auth_headers,
        employee["id"],
        loan_date="2026-07-21",
    )
    client.post(
        f"/api/v1/employees/loans/{voided['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    )
    rejected_voided = _preview_with_loan(
        client,
        api_auth_headers,
        employee["id"],
        voided["id"],
        "1.00",
    )
    assert rejected_voided.status_code == 409


def test_active_deductions_cannot_be_reused_and_void_releases_them(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    created = _create_payroll(
        client,
        api_auth_headers,
        employee["id"],
        advance["id"],
        loan["id"],
    )

    duplicate = client.post(
        "/api/v1/payroll/runs",
        headers=api_auth_headers,
        json=_payroll_payload(
            employee["id"],
            advance_id=advance["id"],
            loan_id=loan["id"],
            include_payroll_date=True,
        ),
    )
    assert duplicate.status_code == 409

    voided = client.post(
        f"/api/v1/payroll/runs/{created['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Rol generado por error"},
    )
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    assert voided.json()["void_reason"] == "Rol generado por error"

    repeated_void = client.post(
        f"/api/v1/payroll/runs/{created['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Segundo intento"},
    )
    assert repeated_void.status_code == 409
    no_reason = client.post(
        f"/api/v1/payroll/runs/{created['id']}/void",
        headers=api_auth_headers,
        json={"reason": "  "},
    )
    assert no_reason.status_code == 422

    reused = _create_payroll(
        client,
        api_auth_headers,
        employee["id"],
        advance["id"],
        loan["id"],
    )
    assert reused["status"] == "active"


def test_employee_payroll_summary_excludes_voided_runs(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    first = _create_payroll(client, api_auth_headers, employee["id"])
    client.post(
        f"/api/v1/payroll/runs/{first['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    )
    active = _create_payroll(client, api_auth_headers, employee["id"])

    response = client.get(
        f"/api/v1/employees/{employee['id']}/payroll-summary",
        headers=api_auth_headers,
        params={"date_from": "2026-07-01", "date_to": "2026-07-31"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == employee["id"]
    assert body["payroll_runs_count"] == 1
    assert body["gross_total"] == active["gross_total"]
    assert body["net_pay_total"] == active["net_pay_total"]
    assert [item["payroll_run_id"] for item in body["latest_payroll_items"]] == [
        active["id"],
    ]


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/payroll/runs/preview", {}),
        ("POST", "/api/v1/payroll/runs", {}),
        ("GET", "/api/v1/payroll/runs", None),
        ("GET", "/api/v1/payroll/runs/1", None),
        ("POST", "/api/v1/payroll/runs/1/void", {"reason": "Error"}),
        ("GET", "/api/v1/employees/1/payroll-summary", None),
    ],
)
def test_payroll_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body,
) -> None:
    client, _ = api_client
    response = client.request(method, path, json=json_body)
    assert response.status_code == 401


def test_payroll_migration_defines_tables_checks_and_indexes(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0023_create_payroll_runs.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0023_payroll",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[str] = []
    created_indexes: list[tuple[str, str]] = []
    table_elements: dict[str, tuple[object, ...]] = {}
    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *elements: (
            created_tables.append(table_name),
            table_elements.update({table_name: elements}),
        ),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda index_name, table_name, columns: created_indexes.append(
            (index_name, table_name),
        ),
    )

    migration.upgrade()

    assert migration.revision == "0023_payroll"
    assert migration.down_revision == "0022_employee_controls"
    assert len(migration.revision) <= 32
    assert created_tables == [
        "payroll_runs",
        "payroll_items",
        "payroll_item_advance_deductions",
        "payroll_item_loan_deductions",
    ]
    assert len(created_indexes) == 13
    assert all(table_elements[table_name] for table_name in created_tables)


def test_payroll_tables_start_empty(api_client) -> None:
    _, testing_session_local = api_client
    assert _payroll_counts(testing_session_local) == (0, 0, 0, 0)


def _create_employee(
    client,
    headers,
    *,
    first_name: str = "Pedro",
    last_name: str = "Zambrano",
    identification: str = "1100000001",
    base_salary: str = "500.00",
    job_position: str = "Chofer",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees",
        headers=headers,
        json={
            "first_name": first_name,
            "last_name": last_name,
            "identification": identification,
            "job_position": job_position,
            "employee_type": "driver",
            "base_salary": base_salary,
            "payment_frequency": "monthly",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_attendance(
    client,
    headers,
    employee_id: int,
    attendance_date: str,
    attendance_status: str,
    hours_worked: str | None,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees/attendance",
        headers=headers,
        json={
            "employee_id": employee_id,
            "attendance_date": attendance_date,
            "status": attendance_status,
            "hours_worked": hours_worked,
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_advance(
    client,
    headers,
    employee_id: int,
    *,
    advance_date: str = "2026-07-18",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees/advances",
        headers=headers,
        json={
            "employee_id": employee_id,
            "advance_date": advance_date,
            "amount": "20.00",
            "reason": "Anticipo de sueldo",
        },
    )
    assert response.status_code == 201
    return response.json()


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
        json={
            "employee_id": employee_id,
            "loan_date": loan_date,
            "principal_amount": principal_amount,
            "reason": "Prestamo interno",
        },
    )
    assert response.status_code == 201
    return response.json()


def _payroll_payload(
    employee_id: int,
    *,
    advance_id: int | None = None,
    loan_id: int | None = None,
    other_deductions: str = "5.00",
    include_payroll_date: bool = False,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "period_start": "2026-07-01",
        "period_end": "2026-07-31",
        "items": [
            {
                "employee_id": employee_id,
                "bonus_amount": "20.00",
                "other_income_amount": "10.00",
                "other_deductions_amount": other_deductions,
                "advance_ids": [advance_id] if advance_id else [],
                "loan_deductions": (
                    [
                        {
                            "employee_loan_id": loan_id,
                            "amount_deducted": "25.00",
                        },
                    ]
                    if loan_id
                    else []
                ),
                "notes": "Rol de prueba",
            },
        ],
    }
    if include_payroll_date:
        payload["payroll_date"] = "2026-07-31"
        payload["notes"] = "Rol julio 2026"
    return payload


def _create_payroll(
    client,
    headers,
    employee_id: int,
    advance_id: int | None = None,
    loan_id: int | None = None,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/payroll/runs",
        headers=headers,
        json=_payroll_payload(
            employee_id,
            advance_id=advance_id,
            loan_id=loan_id,
            include_payroll_date=True,
        ),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _preview_with_advance(client, headers, employee_id: int, advance_id: int):
    return client.post(
        "/api/v1/payroll/runs/preview",
        headers=headers,
        json=_payroll_payload(employee_id, advance_id=advance_id),
    )


def _preview_with_loan(
    client,
    headers,
    employee_id: int,
    loan_id: int,
    amount: str,
):
    payload = _payroll_payload(employee_id)
    payload["items"][0]["loan_deductions"] = [
        {"employee_loan_id": loan_id, "amount_deducted": amount},
    ]
    return client.post(
        "/api/v1/payroll/runs/preview",
        headers=headers,
        json=payload,
    )


def _payroll_counts(testing_session_local) -> tuple[int, int, int, int]:
    with testing_session_local() as session:
        return (
            session.scalar(select(func.count()).select_from(PayrollRun)) or 0,
            session.scalar(select(func.count()).select_from(PayrollItem)) or 0,
            session.scalar(
                select(func.count()).select_from(
                    PayrollItemAdvanceDeduction,
                ),
            )
            or 0,
            session.scalar(
                select(func.count()).select_from(PayrollItemLoanDeduction),
            )
            or 0,
        )


def _protected_counts(testing_session_local) -> tuple[int, int, int]:
    with testing_session_local() as session:
        return (
            session.scalar(select(func.count()).select_from(CashSession)) or 0,
            session.scalar(select(func.count()).select_from(OperatingExpense))
            or 0,
            session.scalar(select(func.count()).select_from(EmployeeLoanPayment))
            or 0,
        )


def _assert_sources_unchanged(
    testing_session_local,
    advance_id: int,
    loan_id: int,
) -> None:
    with testing_session_local() as session:
        advance = session.get(EmployeeAdvance, advance_id)
        loan = session.get(EmployeeLoan, loan_id)
        assert advance is not None
        assert advance.status == "active"
        assert str(advance.amount) == "20.00"
        assert loan is not None
        assert loan.status == "active"
        assert str(loan.paid_amount) == "0.00"
        assert str(loan.balance_amount) == "100.00"
