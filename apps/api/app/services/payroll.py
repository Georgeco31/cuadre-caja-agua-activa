import json
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.employee_advance import EmployeeAdvance
from app.models.employee_attendance import EmployeeAttendance
from app.models.employee_loan import EmployeeLoan
from app.models.payroll_item import PayrollItem
from app.models.payroll_run import PayrollRun
from app.repositories import payroll as payroll_repository
from app.schemas.payroll import (
    PayrollCalculationRequest,
    PayrollItemInput,
    PayrollItemUpdate,
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
    calculation = _empty_calculation(payload.period_start, payload.period_end)
    if payload.employee_ids or payload.items:
        calculation = _calculate_run(
            db,
            PayrollCalculationRequest(
                period_start=payload.period_start,
                period_end=payload.period_end,
                employee_ids=payload.employee_ids,
                items=payload.items,
            ),
            lock_sources=True,
        )
    payroll_date = payload.payroll_date or payload.period_end
    payroll_run = payroll_repository.create_run(
        db,
        {
            "payroll_number": f"PENDING-{uuid4().hex}",
            "label": payload.label,
            "period_start": payload.period_start,
            "period_end": payload.period_end,
            "payroll_date": payroll_date,
            "status": "draft",
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
        _audit(
            db,
            payroll_run.id,
            "run_created",
            created_by,
            details={
                "label": payroll_run.label,
                "period_start": payroll_run.period_start,
                "period_end": payroll_run.period_end,
            },
        )
        for calculated_item in calculation["items"]:
            item = _persist_item(db, payroll_run.id, calculated_item)
            _audit(
                db,
                payroll_run.id,
                "item_added",
                created_by,
                details={
                    "employee_id": item.employee_id,
                    "net_amount": item.net_pay_amount,
                },
            )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo crear el rol de pago.") from error

    return get_run(db, payroll_run.id)


def add_item(
    db: Session,
    payroll_run_id: int,
    payload: PayrollItemInput,
    actor_id: int,
) -> PayrollRun:
    payroll_run = _require_run(db, payroll_run_id, for_update=True)
    _ensure_draft(payroll_run)
    if payroll_repository.get_item_by_run_employee(
        db,
        payroll_run.id,
        payload.employee_id,
    ):
        raise ValueError("El empleado ya está agregado a este rol.")
    calculated = _calculate_single_item(
        db,
        payroll_run,
        payload,
        lock_sources=True,
    )
    _ensure_sources_unique_in_run(payroll_run, calculated)
    try:
        item = _persist_item(db, payroll_run.id, calculated)
        db.flush()
        _refresh_run_totals(db, payroll_run)
        _audit(
            db,
            payroll_run.id,
            "item_added",
            actor_id,
            details={
                "employee_id": item.employee_id,
                "net_amount": item.net_pay_amount,
            },
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo agregar el empleado al rol.") from error
    return get_run(db, payroll_run.id)


def update_item(
    db: Session,
    payroll_item_id: int,
    payload: PayrollItemUpdate,
    actor_id: int,
) -> PayrollRun:
    item = payroll_repository.get_item(
        db,
        payroll_item_id,
        for_update=True,
    )
    if item is None:
        raise ValueError("El ítem del rol no existe.")
    payroll_run = _require_run(db, item.payroll_run_id, for_update=True)
    _ensure_draft(payroll_run)
    item_input = PayrollItemInput(
        employee_id=item.employee_id,
        **payload.model_dump(exclude={"correction_reason"}),
    )
    calculated = _calculate_single_item(
        db,
        payroll_run,
        item_input,
        lock_sources=True,
    )
    _ensure_sources_unique_in_run(
        payroll_run,
        calculated,
        exclude_payroll_item_id=item.id,
    )
    previous_values = _item_audit_values(item)
    try:
        payroll_repository.delete_item_deductions(db, item.id)
        db.flush()
        _apply_calculation_to_item(item, calculated)
        db.add(item)
        db.flush()
        _persist_deductions(db, item.id, calculated)
        db.flush()
        _refresh_run_totals(db, payroll_run)
        _audit(
            db,
            payroll_run.id,
            "item_updated",
            actor_id,
            reason=payload.correction_reason,
            details={
                "employee_id": item.employee_id,
                "before": previous_values,
                "after": _calculation_audit_values(calculated),
            },
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo actualizar el ítem del rol.") from error
    return get_run(db, payroll_run.id)


def approve_run(
    db: Session,
    payroll_run_id: int,
    actor_id: int,
) -> PayrollRun:
    payroll_run = _require_run(db, payroll_run_id, for_update=True)
    _ensure_draft(payroll_run)
    if not payroll_run.items:
        raise ValueError("El rol debe tener al menos un empleado para aprobarse.")
    _validate_run_deduction_sources(db, payroll_run)
    approved_at = datetime.now(timezone.utc)
    payroll_run.status = "approved"
    payroll_run.approved_by = actor_id
    payroll_run.approved_at = approved_at
    db.add(payroll_run)
    _audit(db, payroll_run.id, "approved", actor_id)
    _commit(db, "No se pudo aprobar el rol de pago.")
    return get_run(db, payroll_run.id)


def mark_run_paid(
    db: Session,
    payroll_run_id: int,
    actor_id: int,
) -> PayrollRun:
    payroll_run = _require_run(db, payroll_run_id, for_update=True)
    if payroll_run.status == "paid":
        raise ValueError("El rol ya está marcado como pagado.")
    if payroll_run.status == "cancelled":
        raise ValueError("El rol cancelado no puede marcarse como pagado.")
    if payroll_run.status != "approved":
        raise ValueError("El rol debe aprobarse antes de marcarlo como pagado.")

    applied_at = datetime.now(timezone.utc)
    try:
        for item in payroll_run.items:
            for deduction in item.advance_deductions:
                advance = payroll_repository.get_advance(
                    db,
                    deduction.employee_advance_id,
                    for_update=True,
                )
                if advance is None:
                    raise ValueError("El anticipo seleccionado no existe.")
                if advance.status != "active":
                    raise ValueError(
                        f"El anticipo {advance.advance_number} ya fue "
                        "descontado o anulado.",
                    )
                advance.status = "deducted"
                advance.deducted_at = applied_at
                advance.deducted_by = actor_id
                advance.deducted_payroll_run_id = payroll_run.id
                deduction.applied_at = applied_at
                db.add_all([advance, deduction])

            for deduction in item.loan_deductions:
                loan = payroll_repository.get_loan(
                    db,
                    deduction.employee_loan_id,
                    for_update=True,
                )
                if loan is None:
                    raise ValueError("El préstamo seleccionado no existe.")
                if loan.status != "active":
                    raise ValueError(
                        f"El préstamo {loan.loan_number} no tiene saldo activo.",
                    )
                amount = _money(deduction.amount_deducted)
                if amount > loan.balance_amount:
                    raise ValueError("El descuento supera el saldo disponible.")
                payment = payroll_repository.create_loan_payment(
                    db,
                    {
                        "payment_number": f"PENDING-{uuid4().hex}",
                        "employee_loan_id": loan.id,
                        "employee_id": loan.employee_id,
                        "payroll_run_id": payroll_run.id,
                        "payment_date": payroll_run.payroll_date,
                        "amount": amount,
                        "notes": (
                            "Descuento aplicado por el rol "
                            f"{payroll_run.payroll_number}."
                        ),
                        "status": "active",
                        "created_by": actor_id,
                    },
                )
                loan.paid_amount = _money(loan.paid_amount + amount)
                loan.balance_amount = _money(loan.balance_amount - amount)
                loan.status = (
                    "paid" if loan.balance_amount == ZERO_MONEY else "active"
                )
                db.add(loan)
                db.flush()
                payment.payment_number = (
                    f"ELP-{payment.payment_date:%Y%m%d}-{payment.id:04d}"
                )
                deduction.loan_payment_id = payment.id
                deduction.applied_at = applied_at
                db.add_all([payment, deduction])

        payroll_run.status = "paid"
        payroll_run.paid_by = actor_id
        payroll_run.paid_at = applied_at
        db.add(payroll_run)
        _audit(
            db,
            payroll_run.id,
            "paid",
            actor_id,
            details={
                "advance_total": payroll_run.advances_deducted_total,
                "loan_total": payroll_run.loan_deductions_total,
                "net_total": payroll_run.net_pay_total,
            },
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "No se pudo aplicar los descuentos del rol de pago.",
        ) from error
    return get_run(db, payroll_run.id)


def cancel_run(
    db: Session,
    payroll_run_id: int,
    reason: str,
    actor_id: int,
) -> PayrollRun:
    payroll_run = _require_run(db, payroll_run_id, for_update=True)
    if payroll_run.status == "paid":
        raise ValueError("El rol pagado no puede cancelarse.")
    if payroll_run.status == "cancelled":
        raise ValueError("El rol de pago ya está cancelado.")
    payroll_run.status = "cancelled"
    payroll_run.cancelled_by = actor_id
    payroll_run.cancelled_at = datetime.now(timezone.utc)
    payroll_run.cancellation_reason = reason
    db.add(payroll_run)
    _audit(db, payroll_run.id, "cancelled", actor_id, reason=reason)
    _commit(db, "No se pudo cancelar el rol de pago.")
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
    return _require_run(db, payroll_run_id)


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
    paid_items = payroll_repository.list_employee_payroll_items(
        db,
        employee_id,
        date_from=date_from,
        date_to=date_to,
    )
    advances = payroll_repository.list_active_advances(db, employee_id)
    loans = payroll_repository.list_active_loans(db, employee_id)

    advance_summaries = []
    for advance in advances:
        reservation_run_id = payroll_repository.advance_reservation_run_id(
            db,
            advance.id,
        )
        reserved_amount = (
            _money(advance.amount)
            if reservation_run_id is not None
            else ZERO_MONEY
        )
        advance_summaries.append(
            {
                "id": advance.id,
                "advance_number": advance.advance_number,
                "advance_date": advance.advance_date,
                "amount": _money(advance.amount),
                "reserved_amount": reserved_amount,
                "estimated_balance": _money(advance.amount - reserved_amount),
                "available_for_payroll": reservation_run_id is None,
            }
        )

    loan_summaries = []
    for loan in loans:
        reservation_run_id, reserved_amount = (
            payroll_repository.loan_reservation(db, loan.id)
        )
        reserved_amount = _money(reserved_amount)
        loan_summaries.append(
            {
                "id": loan.id,
                "loan_number": loan.loan_number,
                "loan_date": loan.loan_date,
                "principal_amount": _money(loan.principal_amount),
                "paid_amount": _money(loan.paid_amount),
                "balance_amount": _money(loan.balance_amount),
                "reserved_amount": reserved_amount,
                "estimated_balance": _money(
                    loan.balance_amount - reserved_amount
                ),
                "available_for_payroll": reservation_run_id is None,
            }
        )

    active_advances_total = _sum_money(
        item["amount"] for item in advance_summaries
    )
    active_loans_balance_total = _sum_money(
        item["balance_amount"] for item in loan_summaries
    )
    reserved_advances_total = _sum_money(
        item["reserved_amount"] for item in advance_summaries
    )
    reserved_loans_total = _sum_money(
        item["reserved_amount"] for item in loan_summaries
    )
    return {
        "employee_id": employee.id,
        "employee_name": _employee_name(employee),
        "base_salary": _money(employee.base_salary),
        "active_advances_total": active_advances_total,
        "active_loans_balance_total": active_loans_balance_total,
        "reserved_advances_total": reserved_advances_total,
        "reserved_loans_total": reserved_loans_total,
        "estimated_pending_balance_after_reserved": _money(
            active_advances_total
            + active_loans_balance_total
            - reserved_advances_total
            - reserved_loans_total
        ),
        "advances": advance_summaries,
        "loans": loan_summaries,
        "paid_payroll_runs_count": len(paid_items),
        "gross_paid_total": _sum_money(
            item.gross_amount for item in paid_items
        ),
        "advances_deducted_total": _sum_money(
            item.advances_deducted_amount for item in paid_items
        ),
        "loan_deductions_total": _sum_money(
            item.loan_deductions_amount for item in paid_items
        ),
        "other_deductions_total": _sum_money(
            item.other_deductions_amount for item in paid_items
        ),
        "net_paid_total": _sum_money(
            item.net_pay_amount for item in paid_items
        ),
        "latest_paid_payroll_items": paid_items[:5],
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
    return _calculation_totals(
        payload.period_start,
        payload.period_end,
        calculated_items,
    )


def _calculate_single_item(
    db: Session,
    payroll_run: PayrollRun,
    item_input: PayrollItemInput,
    *,
    lock_sources: bool,
) -> dict[str, object]:
    advances_by_id, loans_by_id = _load_deduction_sources(
        db,
        [item_input],
        lock_sources=lock_sources,
        exclude_payroll_run_id=payroll_run.id,
    )
    return _calculate_item(
        db,
        item_input.employee_id,
        item_input,
        payroll_run.period_start,
        payroll_run.period_end,
        advances_by_id,
        loans_by_id,
        lock_sources=lock_sources,
    )


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
        raise ValueError(f"El empleado {employee_id} está inactivo.")

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
                f"El anticipo {advance.advance_number} pertenece a otro "
                "empleado.",
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
                f"El préstamo {loan.loan_number} pertenece a otro empleado.",
            )
        amount_deducted = _money(deduction_input.amount_deducted)
        if amount_deducted > loan.balance_amount:
            raise ValueError("El descuento supera el saldo disponible.")
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

    base_salary_snapshot = _money(employee.base_salary)
    base_salary_amount = _money(
        item_input.base_salary_amount
        if item_input.base_salary_amount is not None
        else employee.base_salary
    )
    bonus_amount = _money(item_input.bonus_amount)
    other_income_amount = _money(item_input.other_income_amount)
    other_deductions_amount = _money(item_input.other_deductions_amount)
    advances_deducted_amount = _sum_money(
        deduction["amount_deducted"] for deduction in advance_deductions
    )
    loan_deductions_amount = _sum_money(
        deduction["amount_deducted"] for deduction in loan_deductions
    )
    gross_amount = _money(
        base_salary_amount + bonus_amount + other_income_amount
    )
    total_deductions_amount = _money(
        advances_deducted_amount
        + loan_deductions_amount
        + other_deductions_amount,
    )
    net_pay_amount = _money(gross_amount - total_deductions_amount)
    if net_pay_amount < ZERO_MONEY:
        raise ValueError(
            f"El neto a pagar de {_employee_name(employee)} no puede ser "
            "negativo.",
        )

    return {
        "employee_id": employee.id,
        "employee_name_snapshot": _employee_name(employee),
        "employee_identification_snapshot": employee.identification,
        "job_position_snapshot": employee.job_position,
        "payment_frequency_snapshot": employee.payment_frequency,
        "base_salary_snapshot": base_salary_snapshot,
        **attendance_values,
        "base_salary_amount": base_salary_amount,
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
    exclude_payroll_run_id: int | None = None,
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
        raise ValueError("No se puede repetir un préstamo dentro del rol.")

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
                f"El anticipo {advance.advance_number} está anulado.",
            )
        if advance.status == "deducted":
            raise ValueError(
                f"El anticipo {advance.advance_number} ya fue descontado.",
            )
        reserved_run_id = payroll_repository.advance_reservation_run_id(
            db,
            advance.id,
            exclude_payroll_run_id=exclude_payroll_run_id,
        )
        if reserved_run_id is not None:
            raise ValueError(
                f"El anticipo {advance.advance_number} ya está reservado "
                "en otro rol.",
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
            raise ValueError(f"El préstamo {loan_id} no existe.")
        if loan.status == "voided":
            raise ValueError(f"El préstamo {loan.loan_number} está anulado.")
        if loan.status == "paid":
            raise ValueError(f"El préstamo {loan.loan_number} ya está pagado.")
        reserved_run_id, _ = payroll_repository.loan_reservation(
            db,
            loan.id,
            exclude_payroll_run_id=exclude_payroll_run_id,
        )
        if reserved_run_id is not None:
            raise ValueError(
                f"El préstamo {loan.loan_number} ya está reservado en otro "
                "rol.",
            )
        loans_by_id[loan.id] = loan
    return advances_by_id, loans_by_id


def _persist_item(
    db: Session,
    payroll_run_id: int,
    calculation: dict[str, object],
) -> PayrollItem:
    item = payroll_repository.create_item(
        db,
        {
            "payroll_run_id": payroll_run_id,
            **{
                field_name: value
                for field_name, value in calculation.items()
                if field_name not in {"advance_deductions", "loan_deductions"}
            },
        },
    )
    db.flush()
    _persist_deductions(db, item.id, calculation)
    return item


def _persist_deductions(
    db: Session,
    payroll_item_id: int,
    calculation: dict[str, object],
) -> None:
    for deduction in calculation["advance_deductions"]:
        payroll_repository.create_advance_deduction(
            db,
            {"payroll_item_id": payroll_item_id, **deduction},
        )
    for deduction in calculation["loan_deductions"]:
        payroll_repository.create_loan_deduction(
            db,
            {"payroll_item_id": payroll_item_id, **deduction},
        )


def _apply_calculation_to_item(
    item: PayrollItem,
    calculation: dict[str, object],
) -> None:
    for field_name, value in calculation.items():
        if field_name not in {"advance_deductions", "loan_deductions"}:
            setattr(item, field_name, value)


def _refresh_run_totals(db: Session, payroll_run: PayrollRun) -> None:
    db.flush()
    db.expire(payroll_run, ["items"])
    items = payroll_run.items
    payroll_run.employees_count = len(items)
    payroll_run.gross_total = _sum_money(item.gross_amount for item in items)
    payroll_run.bonuses_total = _sum_money(
        item.bonus_amount for item in items
    )
    payroll_run.advances_deducted_total = _sum_money(
        item.advances_deducted_amount for item in items
    )
    payroll_run.loan_deductions_total = _sum_money(
        item.loan_deductions_amount for item in items
    )
    payroll_run.other_deductions_total = _sum_money(
        item.other_deductions_amount for item in items
    )
    payroll_run.total_deductions = _sum_money(
        item.total_deductions_amount for item in items
    )
    payroll_run.net_pay_total = _sum_money(
        item.net_pay_amount for item in items
    )
    db.add(payroll_run)


def _validate_run_deduction_sources(
    db: Session,
    payroll_run: PayrollRun,
) -> None:
    for item in payroll_run.items:
        for deduction in item.advance_deductions:
            advance = payroll_repository.get_advance(
                db,
                deduction.employee_advance_id,
                for_update=True,
            )
            if advance is None or advance.status != "active":
                raise ValueError(
                    "Uno de los anticipos ya no está disponible para "
                    "descuento.",
                )
        for deduction in item.loan_deductions:
            loan = payroll_repository.get_loan(
                db,
                deduction.employee_loan_id,
                for_update=True,
            )
            if loan is None or loan.status != "active":
                raise ValueError(
                    "Uno de los préstamos ya no tiene saldo activo.",
                )
            if deduction.amount_deducted > loan.balance_amount:
                raise ValueError("El descuento supera el saldo disponible.")


def _ensure_sources_unique_in_run(
    payroll_run: PayrollRun,
    calculation: dict[str, object],
    *,
    exclude_payroll_item_id: int | None = None,
) -> None:
    used_advances = {
        deduction.employee_advance_id
        for item in payroll_run.items
        if item.id != exclude_payroll_item_id
        for deduction in item.advance_deductions
    }
    used_loans = {
        deduction.employee_loan_id
        for item in payroll_run.items
        if item.id != exclude_payroll_item_id
        for deduction in item.loan_deductions
    }
    requested_advances = {
        deduction["employee_advance_id"]
        for deduction in calculation["advance_deductions"]
    }
    requested_loans = {
        deduction["employee_loan_id"]
        for deduction in calculation["loan_deductions"]
    }
    if used_advances & requested_advances:
        raise ValueError("El anticipo ya está usado en otro ítem de este rol.")
    if used_loans & requested_loans:
        raise ValueError("El préstamo ya está usado en otro ítem de este rol.")


def _require_run(
    db: Session,
    payroll_run_id: int,
    *,
    for_update: bool = False,
) -> PayrollRun:
    payroll_run = payroll_repository.get_run(
        db,
        payroll_run_id,
        for_update=for_update,
    )
    if payroll_run is None:
        raise ValueError("El rol de pago no existe.")
    return payroll_run


def _ensure_draft(payroll_run: PayrollRun) -> None:
    if payroll_run.status == "paid":
        raise ValueError("El rol pagado no puede modificarse.")
    if payroll_run.status == "approved":
        raise ValueError(
            "El rol aprobado no puede modificarse; cancélalo con motivo "
            "y crea una corrección.",
        )
    if payroll_run.status == "cancelled":
        raise ValueError("El rol cancelado no puede modificarse.")


def _audit(
    db: Session,
    payroll_run_id: int,
    action: str,
    actor_id: int,
    *,
    reason: str | None = None,
    details: dict[str, object] | None = None,
) -> None:
    payroll_repository.create_audit_log(
        db,
        {
            "payroll_run_id": payroll_run_id,
            "action": action,
            "actor_id": actor_id,
            "reason": reason,
            "details": (
                json.dumps(
                    details,
                    ensure_ascii=False,
                    default=str,
                    sort_keys=True,
                )
                if details
                else None
            ),
        },
    )


def _calculation_totals(
    period_start: date,
    period_end: date,
    calculated_items: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "period_start": period_start,
        "period_end": period_end,
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


def _empty_calculation(period_start: date, period_end: date) -> dict[str, object]:
    return _calculation_totals(period_start, period_end, [])


def _item_audit_values(item: PayrollItem) -> dict[str, object]:
    return {
        "base_salary": item.base_salary_amount,
        "bonuses": item.bonus_amount,
        "other_income": item.other_income_amount,
        "advance_deductions": item.advances_deducted_amount,
        "loan_deductions": item.loan_deductions_amount,
        "other_deductions": item.other_deductions_amount,
        "net_amount": item.net_pay_amount,
    }


def _calculation_audit_values(
    calculation: dict[str, object],
) -> dict[str, object]:
    return {
        "base_salary": calculation["base_salary_amount"],
        "bonuses": calculation["bonus_amount"],
        "other_income": calculation["other_income_amount"],
        "advance_deductions": calculation["advances_deducted_amount"],
        "loan_deductions": calculation["loan_deductions_amount"],
        "other_deductions": calculation["other_deductions_amount"],
        "net_amount": calculation["net_pay_amount"],
    }


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


def _commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(message) from error
