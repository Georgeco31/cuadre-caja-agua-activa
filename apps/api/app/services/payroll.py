from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.employee_advance import EmployeeAdvance
from app.models.employee_attendance import EmployeeAttendance
from app.models.employee_loan import EmployeeLoan
from app.models.payroll_run import PayrollRun
from app.repositories import payroll as payroll_repository
from app.schemas.payroll import (
    PayrollCalculationRequest,
    PayrollItemInput,
    PayrollRunCreate,
)

MONEY_QUANTUM = Decimal("0.01")
HOURS_QUANTUM = Decimal("0.01")
ZERO_MONEY = Decimal("0.00")


def preview_run(
    db: Session,
    payload: PayrollCalculationRequest,
) -> dict[str, object]:
    return _calculate_run(db, payload, lock_sources=False)


def create_run(
    db: Session,
    payload: PayrollRunCreate,
    created_by: int,
) -> PayrollRun:
    calculation = _calculate_run(db, payload, lock_sources=True)
    payroll_run = payroll_repository.create_run(
        db,
        {
            "payroll_number": f"PENDING-{uuid4().hex}",
            "period_start": payload.period_start,
            "period_end": payload.period_end,
            "payroll_date": payload.payroll_date,
            "status": "active",
            "employees_count": calculation["employees_count"],
            "gross_total": calculation["gross_total"],
            "bonuses_total": calculation["bonuses_total"],
            "advances_deducted_total": calculation[
                "advances_deducted_total"
            ],
            "loan_deductions_total": calculation["loan_deductions_total"],
            "other_deductions_total": calculation[
                "other_deductions_total"
            ],
            "total_deductions": calculation["total_deductions"],
            "net_pay_total": calculation["net_pay_total"],
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        payroll_run.payroll_number = (
            f"PAY-{payroll_run.payroll_date:%Y%m%d}-{payroll_run.id:04d}"
        )
        for calculated_item in calculation["items"]:
            advance_deductions = calculated_item["advance_deductions"]
            loan_deductions = calculated_item["loan_deductions"]
            item = payroll_repository.create_item(
                db,
                {
                    "payroll_run_id": payroll_run.id,
                    **{
                        field_name: value
                        for field_name, value in calculated_item.items()
                        if field_name
                        not in {"advance_deductions", "loan_deductions"}
                    },
                },
            )
            db.flush()
            for deduction in advance_deductions:
                payroll_repository.create_advance_deduction(
                    db,
                    {
                        "payroll_item_id": item.id,
                        **deduction,
                    },
                )
            for deduction in loan_deductions:
                payroll_repository.create_loan_deduction(
                    db,
                    {
                        "payroll_item_id": item.id,
                        **deduction,
                    },
                )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo crear el rol de pago.") from error

    return get_run(db, payroll_run.id)


def list_runs(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    employee_id: int | None = None,
    search: str | None = None,
) -> list[PayrollRun]:
    _validate_date_range(date_from, date_to)
    normalized_search = search.strip() if search is not None else None
    return payroll_repository.list_runs(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        employee_id=employee_id,
        search=normalized_search or None,
    )


def get_run(db: Session, payroll_run_id: int) -> PayrollRun:
    payroll_run = payroll_repository.get_run(db, payroll_run_id)
    if payroll_run is None:
        raise ValueError("El rol de pago no existe.")
    return payroll_run


def void_run(
    db: Session,
    payroll_run_id: int,
    reason: str,
) -> PayrollRun:
    payroll_run = payroll_repository.get_run(
        db,
        payroll_run_id,
        for_update=True,
    )
    if payroll_run is None:
        raise ValueError("El rol de pago no existe.")
    if payroll_run.status == "voided":
        raise ValueError("El rol de pago ya esta anulado.")
    payroll_repository.mark_voided(
        db,
        payroll_run,
        reason,
        datetime.now(timezone.utc),
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular el rol de pago.") from error
    return get_run(db, payroll_run.id)


def get_employee_payroll_summary(
    db: Session,
    employee_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict[str, object]:
    _validate_date_range(date_from, date_to)
    employee = payroll_repository.get_employee(db, employee_id)
    if employee is None:
        raise ValueError("El empleado no existe.")
    items = payroll_repository.list_employee_payroll_items(
        db,
        employee_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "employee_id": employee.id,
        "employee_name": _employee_name(employee),
        "payroll_runs_count": len(items),
        "gross_total": _sum_money(item.gross_amount for item in items),
        "advances_deducted_total": _sum_money(
            item.advances_deducted_amount for item in items
        ),
        "loan_deductions_total": _sum_money(
            item.loan_deductions_amount for item in items
        ),
        "other_deductions_total": _sum_money(
            item.other_deductions_amount for item in items
        ),
        "net_pay_total": _sum_money(item.net_pay_amount for item in items),
        "latest_payroll_items": items[:5],
    }


def _calculate_run(
    db: Session,
    payload: PayrollCalculationRequest,
    *,
    lock_sources: bool,
) -> dict[str, object]:
    selected_employee_ids, inputs_by_employee = _resolve_items(payload)
    advances_by_id, loans_by_id = _load_deduction_sources(
        db,
        inputs_by_employee.values(),
        lock_sources=lock_sources,
    )
    calculated_items = [
        _calculate_item(
            db,
            employee_id,
            inputs_by_employee.get(
                employee_id,
                PayrollItemInput(employee_id=employee_id),
            ),
            payload.period_start,
            payload.period_end,
            advances_by_id,
            loans_by_id,
            lock_sources=lock_sources,
        )
        for employee_id in selected_employee_ids
    ]
    return {
        "period_start": payload.period_start,
        "period_end": payload.period_end,
        "employees_count": len(calculated_items),
        "gross_total": _sum_money(
            item["gross_amount"] for item in calculated_items
        ),
        "bonuses_total": _sum_money(
            item["bonus_amount"] for item in calculated_items
        ),
        "advances_deducted_total": _sum_money(
            item["advances_deducted_amount"] for item in calculated_items
        ),
        "loan_deductions_total": _sum_money(
            item["loan_deductions_amount"] for item in calculated_items
        ),
        "other_deductions_total": _sum_money(
            item["other_deductions_amount"] for item in calculated_items
        ),
        "total_deductions": _sum_money(
            item["total_deductions_amount"] for item in calculated_items
        ),
        "net_pay_total": _sum_money(
            item["net_pay_amount"] for item in calculated_items
        ),
        "items": calculated_items,
    }


def _calculate_item(
    db: Session,
    employee_id: int,
    item_input: PayrollItemInput,
    period_start: date,
    period_end: date,
    advances_by_id: dict[int, EmployeeAdvance],
    loans_by_id: dict[int, EmployeeLoan],
    *,
    lock_sources: bool,
) -> dict[str, object]:
    employee = payroll_repository.get_employee(
        db,
        employee_id,
        for_update=lock_sources,
    )
    if employee is None:
        raise ValueError(f"El empleado {employee_id} no existe.")
    if not employee.is_active:
        raise ValueError(f"El empleado {employee_id} esta inactivo.")

    attendance = payroll_repository.list_attendance(
        db,
        employee_id,
        period_start,
        period_end,
    )
    attendance_values = _attendance_summary(attendance)
    advance_deductions = []
    for advance_id in item_input.advance_ids:
        advance = advances_by_id[advance_id]
        if advance.employee_id != employee.id:
            raise ValueError(
                f"El anticipo {advance.advance_number} pertenece a otro empleado.",
            )
        advance_deductions.append(
            {
                "employee_advance_id": advance.id,
                "amount_deducted": _money(advance.amount),
                "advance_number_snapshot": advance.advance_number,
                "advance_date_snapshot": advance.advance_date,
                "reason_snapshot": advance.reason,
            },
        )

    loan_deductions = []
    for deduction_input in item_input.loan_deductions:
        loan = loans_by_id[deduction_input.employee_loan_id]
        if loan.employee_id != employee.id:
            raise ValueError(
                f"El prestamo {loan.loan_number} pertenece a otro empleado.",
            )
        amount_deducted = _money(deduction_input.amount_deducted)
        if amount_deducted > loan.balance_amount:
            raise ValueError(
                "El descuento del prestamo no puede superar su saldo actual.",
            )
        loan_deductions.append(
            {
                "employee_loan_id": loan.id,
                "amount_deducted": amount_deducted,
                "loan_number_snapshot": loan.loan_number,
                "loan_date_snapshot": loan.loan_date,
                "loan_balance_snapshot": _money(loan.balance_amount),
                "reason_snapshot": loan.reason,
            },
        )

    base_salary = _money(employee.base_salary)
    bonus_amount = _money(item_input.bonus_amount)
    other_income_amount = _money(item_input.other_income_amount)
    other_deductions_amount = _money(item_input.other_deductions_amount)
    advances_deducted_amount = _sum_money(
        deduction["amount_deducted"] for deduction in advance_deductions
    )
    loan_deductions_amount = _sum_money(
        deduction["amount_deducted"] for deduction in loan_deductions
    )
    gross_amount = _money(base_salary + bonus_amount + other_income_amount)
    total_deductions_amount = _money(
        advances_deducted_amount
        + loan_deductions_amount
        + other_deductions_amount,
    )
    net_pay_amount = _money(gross_amount - total_deductions_amount)
    if net_pay_amount < ZERO_MONEY:
        raise ValueError(
            f"El neto a pagar de {_employee_name(employee)} no puede ser negativo.",
        )

    return {
        "employee_id": employee.id,
        "employee_name_snapshot": _employee_name(employee),
        "employee_identification_snapshot": employee.identification,
        "job_position_snapshot": employee.job_position,
        "payment_frequency_snapshot": employee.payment_frequency,
        "base_salary_snapshot": base_salary,
        **attendance_values,
        # MVP: attendance is a frozen reference; base salary is not prorated.
        "base_salary_amount": base_salary,
        "bonus_amount": bonus_amount,
        "other_income_amount": other_income_amount,
        "gross_amount": gross_amount,
        "advances_deducted_amount": advances_deducted_amount,
        "loan_deductions_amount": loan_deductions_amount,
        "other_deductions_amount": other_deductions_amount,
        "total_deductions_amount": total_deductions_amount,
        "net_pay_amount": net_pay_amount,
        "notes": item_input.notes,
        "advance_deductions": advance_deductions,
        "loan_deductions": loan_deductions,
    }


def _resolve_items(
    payload: PayrollCalculationRequest,
) -> tuple[list[int], dict[int, PayrollItemInput]]:
    items_by_employee = {item.employee_id: item for item in payload.items}
    selected_employee_ids = (
        payload.employee_ids
        if payload.employee_ids
        else [item.employee_id for item in payload.items]
    )
    return selected_employee_ids, items_by_employee


def _load_deduction_sources(
    db: Session,
    item_inputs,
    *,
    lock_sources: bool,
) -> tuple[dict[int, EmployeeAdvance], dict[int, EmployeeLoan]]:
    item_inputs = list(item_inputs)
    advance_ids = [
        advance_id
        for item_input in item_inputs
        for advance_id in item_input.advance_ids
    ]
    loan_ids = [
        deduction.employee_loan_id
        for item_input in item_inputs
        for deduction in item_input.loan_deductions
    ]
    if len(advance_ids) != len(set(advance_ids)):
        raise ValueError("No se puede repetir un anticipo dentro del rol.")
    if len(loan_ids) != len(set(loan_ids)):
        raise ValueError("No se puede repetir un prestamo dentro del rol.")

    advances_by_id: dict[int, EmployeeAdvance] = {}
    for advance_id in sorted(advance_ids):
        advance = payroll_repository.get_advance(
            db,
            advance_id,
            for_update=lock_sources,
        )
        if advance is None:
            raise ValueError(f"El anticipo {advance_id} no existe.")
        if advance.status == "voided":
            raise ValueError(
                f"El anticipo {advance.advance_number} esta anulado.",
            )
        if payroll_repository.advance_is_used_in_active_payroll(db, advance.id):
            raise ValueError(
                f"El anticipo {advance.advance_number} ya fue usado "
                "en un rol activo.",
            )
        advances_by_id[advance.id] = advance

    loans_by_id: dict[int, EmployeeLoan] = {}
    for loan_id in sorted(loan_ids):
        loan = payroll_repository.get_loan(
            db,
            loan_id,
            for_update=lock_sources,
        )
        if loan is None:
            raise ValueError(f"El prestamo {loan_id} no existe.")
        if loan.status == "voided":
            raise ValueError(f"El prestamo {loan.loan_number} esta anulado.")
        if loan.status == "paid":
            raise ValueError(f"El prestamo {loan.loan_number} ya esta pagado.")
        if payroll_repository.loan_is_used_in_active_payroll(db, loan.id):
            raise ValueError(
                f"El prestamo {loan.loan_number} ya fue usado "
                "en un rol activo.",
            )
        loans_by_id[loan.id] = loan
    return advances_by_id, loans_by_id


def _attendance_summary(
    attendance: list[EmployeeAttendance],
) -> dict[str, object]:
    return {
        "attendance_days": sum(
            item.status in {"present", "late"} for item in attendance
        ),
        "absent_days": sum(item.status == "absent" for item in attendance),
        "permission_days": sum(
            item.status == "permission" for item in attendance
        ),
        "vacation_days": sum(
            item.status == "vacation" for item in attendance
        ),
        "sick_days": sum(item.status == "sick" for item in attendance),
        "late_days": sum(item.status == "late" for item in attendance),
        "hours_worked": sum(
            (
                item.hours_worked
                for item in attendance
                if item.hours_worked is not None
            ),
            start=ZERO_MONEY,
        ).quantize(HOURS_QUANTUM),
    }


def _employee_name(employee: Employee) -> str:
    return f"{employee.first_name} {employee.last_name}"


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM)


def _sum_money(values) -> Decimal:
    return sum(values, start=ZERO_MONEY).quantize(MONEY_QUANTUM)


def _validate_date_range(
    date_from: date | None,
    date_to: date | None,
) -> None:
    if date_from is not None and date_to is not None and date_to < date_from:
        raise ValueError(
            "La fecha final no puede ser menor que la fecha inicial.",
        )
