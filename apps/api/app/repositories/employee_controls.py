from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.employee_advance import EmployeeAdvance
from app.models.employee_attendance import EmployeeAttendance
from app.models.employee_loan import EmployeeLoan
from app.models.employee_loan_payment import EmployeeLoanPayment


def get_attendance(
    db: Session,
    attendance_id: int,
) -> EmployeeAttendance | None:
    statement = (
        select(EmployeeAttendance)
        .options(joinedload(EmployeeAttendance.employee))
        .where(EmployeeAttendance.id == attendance_id)
    )
    return db.scalar(statement)


def get_attendance_by_employee_date(
    db: Session,
    employee_id: int,
    attendance_date: date,
    *,
    exclude_attendance_id: int | None = None,
) -> EmployeeAttendance | None:
    statement = select(EmployeeAttendance).where(
        EmployeeAttendance.employee_id == employee_id,
        EmployeeAttendance.attendance_date == attendance_date,
    )
    if exclude_attendance_id is not None:
        statement = statement.where(
            EmployeeAttendance.id != exclude_attendance_id,
        )
    return db.scalar(statement)


def list_attendance(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeAttendance]:
    statement = select(EmployeeAttendance).options(
        joinedload(EmployeeAttendance.employee),
    )
    if date_from is not None:
        statement = statement.where(
            EmployeeAttendance.attendance_date >= date_from,
        )
    if date_to is not None:
        statement = statement.where(
            EmployeeAttendance.attendance_date <= date_to,
        )
    if employee_id is not None:
        statement = statement.where(
            EmployeeAttendance.employee_id == employee_id,
        )
    if status is not None:
        statement = statement.where(EmployeeAttendance.status == status)
    statement = statement.order_by(
        EmployeeAttendance.attendance_date.desc(),
        EmployeeAttendance.id.desc(),
    )
    return list(db.scalars(statement))


def create_attendance(
    db: Session,
    values: dict[str, object],
) -> EmployeeAttendance:
    attendance = EmployeeAttendance(**values)
    db.add(attendance)
    return attendance


def update_attendance(
    db: Session,
    attendance: EmployeeAttendance,
    values: dict[str, object],
) -> EmployeeAttendance:
    _set_values(attendance, values)
    db.add(attendance)
    return attendance


def get_advance(
    db: Session,
    advance_id: int,
    *,
    for_update: bool = False,
) -> EmployeeAdvance | None:
    statement = (
        select(EmployeeAdvance)
        .options(joinedload(EmployeeAdvance.employee))
        .where(EmployeeAdvance.id == advance_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_advances(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeAdvance]:
    statement = select(EmployeeAdvance).options(
        joinedload(EmployeeAdvance.employee),
    )
    if date_from is not None:
        statement = statement.where(EmployeeAdvance.advance_date >= date_from)
    if date_to is not None:
        statement = statement.where(EmployeeAdvance.advance_date <= date_to)
    if employee_id is not None:
        statement = statement.where(EmployeeAdvance.employee_id == employee_id)
    if status is not None:
        statement = statement.where(EmployeeAdvance.status == status)
    statement = statement.order_by(
        EmployeeAdvance.advance_date.desc(),
        EmployeeAdvance.id.desc(),
    )
    return list(db.scalars(statement))


def create_advance(
    db: Session,
    values: dict[str, object],
) -> EmployeeAdvance:
    advance = EmployeeAdvance(**values)
    db.add(advance)
    return advance


def mark_advance_voided(
    db: Session,
    advance: EmployeeAdvance,
    reason: str,
    voided_at: datetime,
) -> EmployeeAdvance:
    advance.status = "voided"
    advance.void_reason = reason
    advance.voided_at = voided_at
    db.add(advance)
    return advance


def get_loan(
    db: Session,
    loan_id: int,
    *,
    for_update: bool = False,
) -> EmployeeLoan | None:
    statement = (
        select(EmployeeLoan)
        .options(joinedload(EmployeeLoan.employee))
        .where(EmployeeLoan.id == loan_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_loans(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeLoan]:
    statement = select(EmployeeLoan).options(joinedload(EmployeeLoan.employee))
    if date_from is not None:
        statement = statement.where(EmployeeLoan.loan_date >= date_from)
    if date_to is not None:
        statement = statement.where(EmployeeLoan.loan_date <= date_to)
    if employee_id is not None:
        statement = statement.where(EmployeeLoan.employee_id == employee_id)
    if status is not None:
        statement = statement.where(EmployeeLoan.status == status)
    statement = statement.order_by(
        EmployeeLoan.loan_date.desc(),
        EmployeeLoan.id.desc(),
    )
    return list(db.scalars(statement))


def create_loan(
    db: Session,
    values: dict[str, object],
) -> EmployeeLoan:
    loan = EmployeeLoan(**values)
    db.add(loan)
    return loan


def mark_loan_voided(
    db: Session,
    loan: EmployeeLoan,
    reason: str,
    voided_at: datetime,
) -> EmployeeLoan:
    loan.status = "voided"
    loan.void_reason = reason
    loan.voided_at = voided_at
    db.add(loan)
    return loan


def has_active_loan_payments(db: Session, loan_id: int) -> bool:
    statement = (
        select(EmployeeLoanPayment.id)
        .where(
            EmployeeLoanPayment.employee_loan_id == loan_id,
            EmployeeLoanPayment.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def get_loan_payment(
    db: Session,
    payment_id: int,
    *,
    for_update: bool = False,
) -> EmployeeLoanPayment | None:
    statement = (
        select(EmployeeLoanPayment)
        .options(
            joinedload(EmployeeLoanPayment.loan),
            joinedload(EmployeeLoanPayment.employee),
        )
        .where(EmployeeLoanPayment.id == payment_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_loan_payments(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    loan_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeLoanPayment]:
    statement = select(EmployeeLoanPayment).options(
        joinedload(EmployeeLoanPayment.loan),
        joinedload(EmployeeLoanPayment.employee),
    )
    if date_from is not None:
        statement = statement.where(
            EmployeeLoanPayment.payment_date >= date_from,
        )
    if date_to is not None:
        statement = statement.where(
            EmployeeLoanPayment.payment_date <= date_to,
        )
    if employee_id is not None:
        statement = statement.where(
            EmployeeLoanPayment.employee_id == employee_id,
        )
    if loan_id is not None:
        statement = statement.where(
            EmployeeLoanPayment.employee_loan_id == loan_id,
        )
    if status is not None:
        statement = statement.where(EmployeeLoanPayment.status == status)
    statement = statement.order_by(
        EmployeeLoanPayment.payment_date.desc(),
        EmployeeLoanPayment.id.desc(),
    )
    return list(db.scalars(statement))


def create_loan_payment(
    db: Session,
    values: dict[str, object],
) -> EmployeeLoanPayment:
    payment = EmployeeLoanPayment(**values)
    db.add(payment)
    return payment


def mark_loan_payment_voided(
    db: Session,
    payment: EmployeeLoanPayment,
    reason: str,
    voided_at: datetime,
) -> EmployeeLoanPayment:
    payment.status = "voided"
    payment.void_reason = reason
    payment.voided_at = voided_at
    db.add(payment)
    return payment


def _set_values(model: object, values: dict[str, object]) -> None:
    for field_name, value in values.items():
        setattr(model, field_name, value)
