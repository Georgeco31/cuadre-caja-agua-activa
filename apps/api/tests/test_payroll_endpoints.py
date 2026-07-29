import importlib.util
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.models.employee_advance import EmployeeAdvance
from app.models.employee_loan import EmployeeLoan
from app.models.employee_loan_payment import EmployeeLoanPayment
from app.models.payroll_audit_log import PayrollAuditLog
from app.models.payroll_item import PayrollItem
from app.models.payroll_item_advance_deduction import (
    PayrollItemAdvanceDeduction,
)
from app.models.payroll_item_loan_deduction import PayrollItemLoanDeduction
from app.models.payroll_run import PayrollRun


def test_admin_creates_empty_draft_with_audit(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client

    response = client.post(
        "/api/v1/payroll/runs",
        headers=api_auth_headers,
        json=_run_payload(),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "draft"
    assert body["label"] == "Julio 2026"
    assert body["employees_count"] == 0
    assert body["gross_total"] == "0.00"
    assert body["net_pay_total"] == "0.00"
    assert body["approved_at"] is None
    assert body["paid_at"] is None
    assert body["cancelled_at"] is None
    assert [log["action"] for log in body["audit_logs"]] == ["run_created"]
    assert _payroll_counts(testing_session_local) == (1, 0, 0, 0, 1)


def test_preview_calculates_backend_net_without_persisting(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])

    response = client.post(
        "/api/v1/payroll/runs/preview",
        headers=api_auth_headers,
        json={
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "items": [
                _item_payload(
                    employee["id"],
                    base_salary="510.00",
                    bonus="20.00",
                    other_income="10.00",
                    other_deductions="5.00",
                    advance_ids=[advance["id"]],
                    loan_id=loan["id"],
                    loan_amount="25.00",
                )
            ],
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["gross_total"] == "540.00"
    assert body["total_deductions"] == "50.00"
    assert body["net_pay_total"] == "490.00"
    assert body["items"][0]["base_salary_snapshot"] == "500.00"
    assert body["items"][0]["base_salary_amount"] == "510.00"
    assert _payroll_counts(testing_session_local) == (0, 0, 0, 0, 0)
    _assert_sources(
        testing_session_local,
        advance["id"],
        loan["id"],
        advance_status="active",
        loan_paid="0.00",
        loan_balance="100.00",
    )


def test_admin_adds_and_updates_employee_only_in_draft(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    run = _create_run(client, api_auth_headers)

    added = client.post(
        f"/api/v1/payroll/runs/{run['id']}/items",
        headers=api_auth_headers,
        json=_item_payload(employee["id"]),
    )

    assert added.status_code == 201, added.text
    added_body = added.json()
    assert added_body["employees_count"] == 1
    item = added_body["items"][0]
    assert item["base_salary_amount"] == "500.00"
    assert item["net_pay_amount"] == "500.00"

    updated = client.patch(
        f"/api/v1/payroll/items/{item['id']}",
        headers=api_auth_headers,
        json={
            **_item_values(
                base_salary="520.00",
                bonus="20.00",
                other_income="10.00",
                other_deductions="5.00",
                advance_ids=[advance["id"]],
                loan_id=loan["id"],
                loan_amount="25.00",
            ),
            "correction_reason": "Ajuste revisado por administración",
        },
    )

    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["gross_total"] == "550.00"
    assert body["total_deductions"] == "50.00"
    assert body["net_pay_total"] == "500.00"
    assert [log["action"] for log in body["audit_logs"]] == [
        "run_created",
        "item_added",
        "item_updated",
    ]
    assert body["audit_logs"][-1]["reason"] == (
        "Ajuste revisado por administración"
    )


@pytest.mark.parametrize(
    "field",
    [
        "base_salary_amount",
        "bonus_amount",
        "other_income_amount",
        "other_deductions_amount",
    ],
)
def test_payroll_rejects_negative_amounts(
    api_client,
    api_auth_headers,
    field: str,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    payload = _item_payload(employee["id"])
    payload[field] = "-0.01"

    response = client.post(
        "/api/v1/payroll/runs/preview",
        headers=api_auth_headers,
        json={
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "items": [payload],
        },
    )

    assert response.status_code == 422


def test_approve_locks_role_and_records_audit(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    run = _create_run_with_item(client, api_auth_headers, employee["id"])

    approved = client.post(
        f"/api/v1/payroll/runs/{run['id']}/approve",
        headers=api_auth_headers,
    )

    assert approved.status_code == 200, approved.text
    body = approved.json()
    assert body["status"] == "approved"
    assert body["approved_by"] is not None
    assert body["approved_at"] is not None
    assert body["audit_logs"][-1]["action"] == "approved"

    changed = client.patch(
        f"/api/v1/payroll/items/{body['items'][0]['id']}",
        headers=api_auth_headers,
        json={
            **_item_values(),
            "correction_reason": "Intento posterior a aprobación",
        },
    )
    assert changed.status_code == 409
    assert "aprobado no puede modificarse" in changed.json()["detail"]


def test_mark_paid_applies_advance_and_loan_once_with_traceability(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    run = _create_run_with_item(
        client,
        api_auth_headers,
        employee["id"],
        advance_id=advance["id"],
        loan_id=loan["id"],
        loan_amount="25.00",
    )

    _approve(client, api_auth_headers, run["id"])
    paid = client.post(
        f"/api/v1/payroll/runs/{run['id']}/mark-paid",
        headers=api_auth_headers,
    )

    assert paid.status_code == 200, paid.text
    body = paid.json()
    assert body["status"] == "paid"
    assert body["paid_by"] is not None
    assert body["paid_at"] is not None
    assert body["audit_logs"][-1]["action"] == "paid"
    assert body["items"][0]["advance_deductions"][0]["applied_at"] is not None
    loan_deduction = body["items"][0]["loan_deductions"][0]
    assert loan_deduction["applied_at"] is not None
    assert loan_deduction["loan_payment_id"] is not None
    _assert_sources(
        testing_session_local,
        advance["id"],
        loan["id"],
        advance_status="deducted",
        loan_paid="25.00",
        loan_balance="75.00",
    )
    with testing_session_local() as session:
        payment = session.scalar(select(EmployeeLoanPayment))
        assert payment is not None
        assert str(payment.amount) == "25.00"
        assert payment.payroll_run_id == run["id"]
        assert payment.status == "active"

    duplicate = client.post(
        f"/api/v1/payroll/runs/{run['id']}/mark-paid",
        headers=api_auth_headers,
    )
    assert duplicate.status_code == 409
    _assert_sources(
        testing_session_local,
        advance["id"],
        loan["id"],
        advance_status="deducted",
        loan_paid="25.00",
        loan_balance="75.00",
    )


def test_paid_role_cannot_be_changed_cancelled_or_have_payment_voided(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    run = _create_run_with_item(
        client,
        api_auth_headers,
        employee["id"],
        advance_id=advance["id"],
        loan_id=loan["id"],
    )
    _approve(client, api_auth_headers, run["id"])
    paid = _mark_paid(client, api_auth_headers, run["id"])
    item_id = paid["items"][0]["id"]

    changed = client.patch(
        f"/api/v1/payroll/items/{item_id}",
        headers=api_auth_headers,
        json={
            **_item_values(),
            "correction_reason": "Intento sobre pagado",
        },
    )
    cancelled = client.post(
        f"/api/v1/payroll/runs/{run['id']}/cancel",
        headers=api_auth_headers,
        json={"reason": "Intento sobre pagado"},
    )
    voided_advance = client.post(
        f"/api/v1/employees/advances/{advance['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Intento sobre aplicado"},
    )
    with testing_session_local() as session:
        payment_id = session.scalar(select(EmployeeLoanPayment.id))
    voided_payment = client.post(
        f"/api/v1/employees/loan-payments/{payment_id}/void",
        headers=api_auth_headers,
        json={"reason": "Intento sobre aplicado"},
    )

    assert changed.status_code == 409
    assert changed.json()["detail"] == "El rol pagado no puede modificarse."
    assert cancelled.status_code == 409
    assert voided_advance.status_code == 409
    assert voided_payment.status_code == 409


def test_cancel_requires_reason_releases_reservations_and_changes_no_balance(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    run = _create_run_with_item(
        client,
        api_auth_headers,
        employee["id"],
        advance_id=advance["id"],
        loan_id=loan["id"],
    )

    no_reason = client.post(
        f"/api/v1/payroll/runs/{run['id']}/cancel",
        headers=api_auth_headers,
        json={"reason": "  "},
    )
    assert no_reason.status_code == 422

    cancelled = client.post(
        f"/api/v1/payroll/runs/{run['id']}/cancel",
        headers=api_auth_headers,
        json={"reason": "Período creado por error"},
    )
    assert cancelled.status_code == 200, cancelled.text
    body = cancelled.json()
    assert body["status"] == "cancelled"
    assert body["cancellation_reason"] == "Período creado por error"
    assert body["cancelled_by"] is not None
    assert body["audit_logs"][-1]["action"] == "cancelled"
    _assert_sources(
        testing_session_local,
        advance["id"],
        loan["id"],
        advance_status="active",
        loan_paid="0.00",
        loan_balance="100.00",
    )

    reused = _create_run_with_item(
        client,
        api_auth_headers,
        employee["id"],
        advance_id=advance["id"],
        loan_id=loan["id"],
    )
    assert reused["status"] == "draft"


def test_sources_reserved_by_draft_cannot_be_used_in_another_run(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    _create_run_with_item(
        client,
        api_auth_headers,
        employee["id"],
        advance_id=advance["id"],
        loan_id=loan["id"],
    )

    duplicate_run = _create_run(client, api_auth_headers)
    duplicate = client.post(
        f"/api/v1/payroll/runs/{duplicate_run['id']}/items",
        headers=api_auth_headers,
        json=_item_payload(
            employee["id"],
            advance_ids=[advance["id"]],
            loan_id=loan["id"],
        ),
    )

    assert duplicate.status_code == 409
    assert "reservado" in duplicate.json()["detail"]


def test_loan_deduction_cannot_exceed_current_balance(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    loan = _create_loan(
        client,
        api_auth_headers,
        employee["id"],
        principal_amount="40.00",
    )
    run = _create_run(client, api_auth_headers)

    response = client.post(
        f"/api/v1/payroll/runs/{run['id']}/items",
        headers=api_auth_headers,
        json=_item_payload(
            employee["id"],
            loan_id=loan["id"],
            loan_amount="40.01",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "El descuento supera el saldo disponible."
    )


def test_employee_summary_shows_pending_reserved_and_paid_values(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    employee = _create_employee(client, api_auth_headers)
    advance = _create_advance(client, api_auth_headers, employee["id"])
    loan = _create_loan(client, api_auth_headers, employee["id"])
    run = _create_run_with_item(
        client,
        api_auth_headers,
        employee["id"],
        advance_id=advance["id"],
        loan_id=loan["id"],
        loan_amount="25.00",
    )

    reserved = client.get(
        f"/api/v1/payroll/employees/{employee['id']}/summary",
        headers=api_auth_headers,
    )
    assert reserved.status_code == 200, reserved.text
    reserved_body = reserved.json()
    assert reserved_body["base_salary"] == "500.00"
    assert reserved_body["active_advances_total"] == "20.00"
    assert reserved_body["active_loans_balance_total"] == "100.00"
    assert reserved_body["reserved_advances_total"] == "20.00"
    assert reserved_body["reserved_loans_total"] == "25.00"
    assert reserved_body["estimated_pending_balance_after_reserved"] == "75.00"
    assert reserved_body["paid_payroll_runs_count"] == 0

    _approve(client, api_auth_headers, run["id"])
    _mark_paid(client, api_auth_headers, run["id"])
    paid = client.get(
        f"/api/v1/payroll/employees/{employee['id']}/summary",
        headers=api_auth_headers,
    )
    assert paid.status_code == 200, paid.text
    paid_body = paid.json()
    assert paid_body["active_advances_total"] == "0.00"
    assert paid_body["active_loans_balance_total"] == "75.00"
    assert paid_body["reserved_advances_total"] == "0.00"
    assert paid_body["reserved_loans_total"] == "0.00"
    assert paid_body["paid_payroll_runs_count"] == 1
    assert paid_body["advances_deducted_total"] == "20.00"
    assert paid_body["loan_deductions_total"] == "25.00"
    assert paid_body["net_paid_total"] == "455.00"


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("GET", "/api/v1/payroll/runs", None),
        (
            "POST",
            "/api/v1/payroll/runs",
            {
                "period_start": "2026-07-01",
                "period_end": "2026-07-31",
                "label": "Julio 2026",
            },
        ),
        ("POST", "/api/v1/payroll/runs/1/items", {"employee_id": 1}),
        ("PATCH", "/api/v1/payroll/items/1", {}),
        ("POST", "/api/v1/payroll/runs/1/approve", None),
        ("POST", "/api/v1/payroll/runs/1/mark-paid", None),
        (
            "POST",
            "/api/v1/payroll/runs/1/cancel",
            {"reason": "No autorizado"},
        ),
        ("GET", "/api/v1/payroll/employees/1/summary", None),
    ],
)
def test_operator_cannot_access_payroll(
    api_client,
    api_operator_auth_headers,
    method: str,
    path: str,
    body,
) -> None:
    client, _ = api_client
    response = client.request(
        method,
        path,
        headers=api_operator_auth_headers,
        json=body,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == (
        "No tienes permiso para gestionar roles de pago."
    )


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("GET", "/api/v1/payroll/runs", None),
        (
            "POST",
            "/api/v1/payroll/runs",
            {
                "period_start": "2026-07-01",
                "period_end": "2026-07-31",
                "label": "Julio 2026",
            },
        ),
        ("POST", "/api/v1/payroll/runs/1/approve", None),
        ("POST", "/api/v1/payroll/runs/1/mark-paid", None),
        (
            "POST",
            "/api/v1/payroll/runs/1/cancel",
            {"reason": "Sin sesión"},
        ),
    ],
)
def test_payroll_requires_authentication(
    api_client,
    method: str,
    path: str,
    body,
) -> None:
    client, _ = api_client
    response = client.request(method, path, json=body)
    assert response.status_code == 401


def test_missing_run_item_and_employee_return_404(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    missing_run = client.get(
        "/api/v1/payroll/runs/999",
        headers=api_auth_headers,
    )
    missing_item = client.patch(
        "/api/v1/payroll/items/999",
        headers=api_auth_headers,
        json={
            **_item_values(),
            "correction_reason": "Ítem inexistente",
        },
    )
    missing_employee = client.get(
        "/api/v1/payroll/employees/999/summary",
        headers=api_auth_headers,
    )
    assert missing_run.status_code == 404
    assert missing_item.status_code == 404
    assert missing_employee.status_code == 404


def test_payroll_migration_follows_0027_and_defines_workflow() -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0028_payroll_base_improvements.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0028_payroll",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    source = migration_path.read_text(encoding="utf-8")
    assert migration.revision == "0028_payroll_base"
    assert migration.down_revision == "0027_sale_date_corrections"
    assert "payroll_audit_logs" in source
    assert "draft', 'approved', 'paid', 'cancelled" in source
    assert "existen roles pagados" in source


def _run_payload() -> dict[str, object]:
    return {
        "period_start": "2026-07-01",
        "period_end": "2026-07-31",
        "payroll_date": "2026-07-31",
        "label": "Julio 2026",
        "notes": "Piloto controlado",
    }


def _item_values(
    *,
    base_salary: str = "500.00",
    bonus: str = "0.00",
    other_income: str = "0.00",
    other_deductions: str = "0.00",
    advance_ids: list[int] | None = None,
    loan_id: int | None = None,
    loan_amount: str = "25.00",
) -> dict[str, object]:
    return {
        "base_salary_amount": base_salary,
        "bonus_amount": bonus,
        "other_income_amount": other_income,
        "other_deductions_amount": other_deductions,
        "advance_ids": advance_ids or [],
        "loan_deductions": (
            [
                {
                    "employee_loan_id": loan_id,
                    "amount_deducted": loan_amount,
                }
            ]
            if loan_id is not None
            else []
        ),
        "notes": "Rol de prueba",
    }


def _item_payload(
    employee_id: int,
    **kwargs,
) -> dict[str, object]:
    return {"employee_id": employee_id, **_item_values(**kwargs)}


def _create_employee(
    client,
    headers,
    *,
    identification: str = "1100000001",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees",
        headers=headers,
        json={
            "first_name": "Pedro",
            "last_name": "Zambrano",
            "identification": identification,
            "job_position": "Chofer",
            "employee_type": "driver",
            "base_salary": "500.00",
            "payment_frequency": "monthly",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_advance(client, headers, employee_id: int) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees/advances",
        headers=headers,
        json={
            "employee_id": employee_id,
            "advance_date": "2026-07-18",
            "amount": "20.00",
            "reason": "Anticipo de sueldo",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_loan(
    client,
    headers,
    employee_id: int,
    *,
    principal_amount: str = "100.00",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/employees/loans",
        headers=headers,
        json={
            "employee_id": employee_id,
            "loan_date": "2026-07-18",
            "principal_amount": principal_amount,
            "reason": "Préstamo interno",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_run(client, headers) -> dict[str, object]:
    response = client.post(
        "/api/v1/payroll/runs",
        headers=headers,
        json=_run_payload(),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_run_with_item(
    client,
    headers,
    employee_id: int,
    *,
    advance_id: int | None = None,
    loan_id: int | None = None,
    loan_amount: str = "25.00",
) -> dict[str, object]:
    run = _create_run(client, headers)
    response = client.post(
        f"/api/v1/payroll/runs/{run['id']}/items",
        headers=headers,
        json=_item_payload(
            employee_id,
            advance_ids=[advance_id] if advance_id is not None else [],
            loan_id=loan_id,
            loan_amount=loan_amount,
        ),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _approve(client, headers, payroll_run_id: int) -> dict[str, object]:
    response = client.post(
        f"/api/v1/payroll/runs/{payroll_run_id}/approve",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _mark_paid(client, headers, payroll_run_id: int) -> dict[str, object]:
    response = client.post(
        f"/api/v1/payroll/runs/{payroll_run_id}/mark-paid",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _payroll_counts(testing_session_local) -> tuple[int, int, int, int, int]:
    with testing_session_local() as session:
        return (
            session.scalar(select(func.count()).select_from(PayrollRun)) or 0,
            session.scalar(select(func.count()).select_from(PayrollItem)) or 0,
            session.scalar(
                select(func.count()).select_from(
                    PayrollItemAdvanceDeduction,
                )
            )
            or 0,
            session.scalar(
                select(func.count()).select_from(
                    PayrollItemLoanDeduction,
                )
            )
            or 0,
            session.scalar(
                select(func.count()).select_from(PayrollAuditLog)
            )
            or 0,
        )


def _assert_sources(
    testing_session_local,
    advance_id: int,
    loan_id: int,
    *,
    advance_status: str,
    loan_paid: str,
    loan_balance: str,
) -> None:
    with testing_session_local() as session:
        advance = session.get(EmployeeAdvance, advance_id)
        loan = session.get(EmployeeLoan, loan_id)
        assert advance is not None
        assert loan is not None
        assert advance.status == advance_status
        assert str(loan.paid_amount) == loan_paid
        assert str(loan.balance_amount) == loan_balance
