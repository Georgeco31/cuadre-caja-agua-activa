from datetime import date
from decimal import Decimal

from sqlalchemy import delete, exists, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.employee import Employee
from app.models.employee_advance import EmployeeAdvance
from app.models.employee_attendance import EmployeeAttendance
from app.models.employee_loan import EmployeeLoan
from app.models.employee_loan_payment import EmployeeLoanPayment
from app.models.payroll_audit_log import PayrollAuditLog
from app.models.payroll_item import PayrollItem
from app.models.payroll_item_advance_deduction import (
    PayrollItemAdvanceDeduction,
)
from app.models.payroll_item_loan_deduction import PayrollItemLoanDeduction
from app.models.payroll_run import PayrollRun


RESERVING_STATUSES = ("draft", "approved")


def get_employee(
    db: Session,
    employee_id: int,
    *,
    for_update: bool = False,
) -> Employee | None:
    statement = select(Employee).where(Employee.id == employee_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_attendance(
    db: Session,
    employee_id: int,
    period_start: date,
    period_end: date,
) -> list[EmployeeAttendance]:
    statement = (
        select(EmployeeAttendance)
        .where(
            EmployeeAttendance.employee_id == employee_id,
            EmployeeAttendance.attendance_date >= period_start,
            EmployeeAttendance.attendance_date <= period_end,
        )
        .order_by(EmployeeAttendance.attendance_date, EmployeeAttendance.id)
    )
    return list(db.scalars(statement))


def get_advance(
    db: Session,
    advance_id: int,
    *,
    for_update: bool = False,
) -> EmployeeAdvance | None:
    statement = select(EmployeeAdvance).where(EmployeeAdvance.id == advance_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def get_loan(
    db: Session,
    loan_id: int,
    *,
    for_update: bool = False,
) -> EmployeeLoan | None:
    statement = select(EmployeeLoan).where(EmployeeLoan.id == loan_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def advance_reservation_run_id(
    db: Session,
    advance_id: int,
    *,
    exclude_payroll_run_id: int | None = None,
) -> int | None:
    statement = (
        select(PayrollRun.id)
        .join(PayrollItem, PayrollItem.payroll_run_id == PayrollRun.id)
        .join(
            PayrollItemAdvanceDeduction,
            PayrollItemAdvanceDeduction.payroll_item_id == PayrollItem.id,
        )
        .where(
            PayrollItemAdvanceDeduction.employee_advance_id == advance_id,
            PayrollRun.status.in_(RESERVING_STATUSES),
        )
        .limit(1)
    )
    if exclude_payroll_run_id is not None:
        statement = statement.where(PayrollRun.id != exclude_payroll_run_id)
    return db.scalar(statement)


def loan_reservation(
    db: Session,
    loan_id: int,
    *,
    exclude_payroll_run_id: int | None = None,
) -> tuple[int | None, Decimal]:
    statement = (
        select(
            PayrollRun.id,
            PayrollItemLoanDeduction.amount_deducted,
        )
        .join(PayrollItem, PayrollItem.payroll_run_id == PayrollRun.id)
        .join(
            PayrollItemLoanDeduction,
            PayrollItemLoanDeduction.payroll_item_id == PayrollItem.id,
        )
        .where(
            PayrollItemLoanDeduction.employee_loan_id == loan_id,
            PayrollRun.status.in_(RESERVING_STATUSES),
        )
        .limit(1)
    )
    if exclude_payroll_run_id is not None:
        statement = statement.where(PayrollRun.id != exclude_payroll_run_id)
    row = db.execute(statement).first()
    if row is None:
        return None, Decimal("0.00")
    return row[0], row[1]


def create_run(db: Session, values: dict[str, object]) -> PayrollRun:
    payroll_run = PayrollRun(**values)
    db.add(payroll_run)
    return payroll_run


def create_item(db: Session, values: dict[str, object]) -> PayrollItem:
    item = PayrollItem(**values)
    db.add(item)
    return item


def get_item(
    db: Session,
    payroll_item_id: int,
    *,
    for_update: bool = False,
) -> PayrollItem | None:
    statement = (
        select(PayrollItem)
        .options(
            selectinload(PayrollItem.advance_deductions),
            selectinload(PayrollItem.loan_deductions),
        )
        .where(PayrollItem.id == payroll_item_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def get_item_by_run_employee(
    db: Session,
    payroll_run_id: int,
    employee_id: int,
) -> PayrollItem | None:
    return db.scalar(
        select(PayrollItem).where(
            PayrollItem.payroll_run_id == payroll_run_id,
            PayrollItem.employee_id == employee_id,
        )
    )


def create_advance_deduction(
    db: Session,
    values: dict[str, object],
) -> PayrollItemAdvanceDeduction:
    deduction = PayrollItemAdvanceDeduction(**values)
    db.add(deduction)
    return deduction


def create_loan_deduction(
    db: Session,
    values: dict[str, object],
) -> PayrollItemLoanDeduction:
    deduction = PayrollItemLoanDeduction(**values)
    db.add(deduction)
    return deduction


def delete_item_deductions(db: Session, payroll_item_id: int) -> None:
    db.execute(
        delete(PayrollItemAdvanceDeduction).where(
            PayrollItemAdvanceDeduction.payroll_item_id == payroll_item_id
        )
    )
    db.execute(
        delete(PayrollItemLoanDeduction).where(
            PayrollItemLoanDeduction.payroll_item_id == payroll_item_id
        )
    )


def create_audit_log(
    db: Session,
    values: dict[str, object],
) -> PayrollAuditLog:
    audit_log = PayrollAuditLog(**values)
    db.add(audit_log)
    return audit_log


def create_loan_payment(
    db: Session,
    values: dict[str, object],
) -> EmployeeLoanPayment:
    payment = EmployeeLoanPayment(**values)
    db.add(payment)
    return payment


def get_run(
    db: Session,
    payroll_run_id: int,
    *,
    for_update: bool = False,
) -> PayrollRun | None:
    statement = (
        select(PayrollRun)
        .options(*_run_options())
        .where(PayrollRun.id == payroll_run_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_runs(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    employee_id: int | None = None,
    search: str | None = None,
) -> list[PayrollRun]:
    statement = select(PayrollRun)
    if date_from is not None:
        statement = statement.where(PayrollRun.payroll_date >= date_from)
    if date_to is not None:
        statement = statement.where(PayrollRun.payroll_date <= date_to)
    if status is not None:
        statement = statement.where(PayrollRun.status == status)
    if employee_id is not None:
        statement = statement.where(
            exists(
                select(PayrollItem.id).where(
                    PayrollItem.payroll_run_id == PayrollRun.id,
                    PayrollItem.employee_id == employee_id,
                ),
            ),
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                PayrollRun.payroll_number.ilike(search_pattern),
                PayrollRun.label.ilike(search_pattern),
                PayrollRun.notes.ilike(search_pattern),
                exists(
                    select(PayrollItem.id).where(
                        PayrollItem.payroll_run_id == PayrollRun.id,
                        or_(
                            PayrollItem.employee_name_snapshot.ilike(
                                search_pattern,
                            ),
                            PayrollItem.employee_identification_snapshot.ilike(
                                search_pattern,
                            ),
                        ),
                    ),
                ),
            ),
        )
    statement = statement.order_by(
        PayrollRun.payroll_date.desc(),
        PayrollRun.id.desc(),
    )
    return list(db.scalars(statement))


def list_employee_payroll_items(
    db: Session,
    employee_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[PayrollItem]:
    statement = (
        select(PayrollItem)
        .join(PayrollRun, PayrollRun.id == PayrollItem.payroll_run_id)
        .options(
            selectinload(PayrollItem.advance_deductions),
            selectinload(PayrollItem.loan_deductions),
        )
        .where(
            PayrollItem.employee_id == employee_id,
            PayrollRun.status == "paid",
        )
    )
    if date_from is not None:
        statement = statement.where(PayrollRun.payroll_date >= date_from)
    if date_to is not None:
        statement = statement.where(PayrollRun.payroll_date <= date_to)
    statement = statement.order_by(
        PayrollRun.payroll_date.desc(),
        PayrollItem.id.desc(),
    )
    return list(db.scalars(statement))


def list_active_advances(
    db: Session,
    employee_id: int,
) -> list[EmployeeAdvance]:
    return list(
        db.scalars(
            select(EmployeeAdvance)
            .where(
                EmployeeAdvance.employee_id == employee_id,
                EmployeeAdvance.status == "active",
            )
            .order_by(EmployeeAdvance.advance_date, EmployeeAdvance.id)
        )
    )


def list_active_loans(
    db: Session,
    employee_id: int,
) -> list[EmployeeLoan]:
    return list(
        db.scalars(
            select(EmployeeLoan)
            .where(
                EmployeeLoan.employee_id == employee_id,
                EmployeeLoan.status == "active",
            )
            .order_by(EmployeeLoan.loan_date, EmployeeLoan.id)
        )
    )


def _run_options():
    return (
        selectinload(PayrollRun.items).selectinload(
            PayrollItem.advance_deductions,
        ),
        selectinload(PayrollRun.items).selectinload(
            PayrollItem.loan_deductions,
        ),
        selectinload(PayrollRun.audit_logs),
    )
