from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.employee_advance import EmployeeAdvance
from app.models.employee_attendance import EmployeeAttendance
from app.models.employee_loan import EmployeeLoan
from app.models.employee_loan_payment import EmployeeLoanPayment
from app.repositories import employee_controls as control_repository
from app.repositories import employees as employee_repository
from app.schemas.employee_controls import (
    EmployeeAdvanceCreate,
    EmployeeAttendanceCreate,
    EmployeeAttendanceUpdate,
    EmployeeLoanCreate,
    EmployeeLoanPaymentCreate,
)

MONEY_QUANTUM = Decimal("0.01")
HOURS_QUANTUM = Decimal("0.01")
ZERO_MONEY = Decimal("0.00")


def create_attendance(
    db: Session,
    payload: EmployeeAttendanceCreate,
    created_by: int,
) -> EmployeeAttendance:
    _get_active_employee(db, payload.employee_id)
    _ensure_attendance_is_available(
        db,
        payload.employee_id,
        payload.attendance_date,
    )
    values = payload.model_dump()
    if values["hours_worked"] is not None:
        values["hours_worked"] = values["hours_worked"].quantize(HOURS_QUANTUM)
    attendance = control_repository.create_attendance(
        db,
        {**values, "created_by": created_by},
    )
    _commit_attendance(db)
    return _require_attendance(db, attendance.id)


def list_attendance(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeAttendance]:
    _validate_date_range(date_from, date_to)
    return control_repository.list_attendance(
        db=db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
        status=status,
    )


def get_attendance(db: Session, attendance_id: int) -> EmployeeAttendance:
    return _require_attendance(db, attendance_id)


def update_attendance(
    db: Session,
    attendance_id: int,
    payload: EmployeeAttendanceUpdate,
) -> EmployeeAttendance:
    attendance = _require_attendance(db, attendance_id)
    values = payload.model_dump(exclude_unset=True)
    attendance_date = values.get(
        "attendance_date",
        attendance.attendance_date,
    )
    if attendance_date != attendance.attendance_date:
        _ensure_attendance_is_available(
            db,
            attendance.employee_id,
            attendance_date,
            exclude_attendance_id=attendance.id,
        )
    if "hours_worked" in values and values["hours_worked"] is not None:
        values["hours_worked"] = values["hours_worked"].quantize(HOURS_QUANTUM)
    control_repository.update_attendance(db, attendance, values)
    _commit_attendance(db)
    return _require_attendance(db, attendance.id)


def create_advance(
    db: Session,
    payload: EmployeeAdvanceCreate,
    created_by: int,
) -> EmployeeAdvance:
    _get_active_employee(db, payload.employee_id)
    advance = control_repository.create_advance(
        db,
        {
            **payload.model_dump(),
            "advance_number": f"PENDING-{uuid4().hex}",
            "amount": payload.amount.quantize(MONEY_QUANTUM),
            "status": "active",
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        advance.advance_number = (
            f"ADV-{advance.advance_date:%Y%m%d}-{advance.id:04d}"
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar el anticipo.") from error
    return _require_advance(db, advance.id)


def list_advances(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeAdvance]:
    _validate_date_range(date_from, date_to)
    return control_repository.list_advances(
        db=db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
        status=status,
    )


def get_advance(db: Session, advance_id: int) -> EmployeeAdvance:
    return _require_advance(db, advance_id)


def void_advance(
    db: Session,
    advance_id: int,
    reason: str,
) -> EmployeeAdvance:
    advance = control_repository.get_advance(db, advance_id, for_update=True)
    if advance is None:
        raise ValueError("El anticipo no existe.")
    if advance.status == "voided":
        raise ValueError("El anticipo ya esta anulado.")
    control_repository.mark_advance_voided(
        db,
        advance,
        reason,
        datetime.now(timezone.utc),
    )
    _commit(db, "No se pudo anular el anticipo.")
    return _require_advance(db, advance.id)


def create_loan(
    db: Session,
    payload: EmployeeLoanCreate,
    created_by: int,
) -> EmployeeLoan:
    _get_active_employee(db, payload.employee_id)
    principal_amount = payload.principal_amount.quantize(MONEY_QUANTUM)
    loan = control_repository.create_loan(
        db,
        {
            **payload.model_dump(),
            "loan_number": f"PENDING-{uuid4().hex}",
            "principal_amount": principal_amount,
            "paid_amount": ZERO_MONEY,
            "balance_amount": principal_amount,
            "status": "active",
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        loan.loan_number = f"LOAN-{loan.loan_date:%Y%m%d}-{loan.id:04d}"
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar el prestamo.") from error
    return _require_loan(db, loan.id)


def list_loans(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeLoan]:
    _validate_date_range(date_from, date_to)
    return control_repository.list_loans(
        db=db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
        status=status,
    )


def get_loan(db: Session, loan_id: int) -> EmployeeLoan:
    return _require_loan(db, loan_id)


def void_loan(
    db: Session,
    loan_id: int,
    reason: str,
) -> EmployeeLoan:
    loan = control_repository.get_loan(db, loan_id, for_update=True)
    if loan is None:
        raise ValueError("El prestamo no existe.")
    if loan.status == "voided":
        raise ValueError("El prestamo ya esta anulado.")
    if control_repository.has_active_loan_payments(db, loan.id):
        raise ValueError(
            "No se puede anular un prestamo con pagos activos.",
        )
    control_repository.mark_loan_voided(
        db,
        loan,
        reason,
        datetime.now(timezone.utc),
    )
    _commit(db, "No se pudo anular el prestamo.")
    return _require_loan(db, loan.id)


def create_loan_payment(
    db: Session,
    loan_id: int,
    payload: EmployeeLoanPaymentCreate,
    created_by: int,
) -> EmployeeLoanPayment:
    loan = control_repository.get_loan(db, loan_id, for_update=True)
    if loan is None:
        raise ValueError("El prestamo no existe.")
    if loan.status == "voided":
        raise ValueError("No se puede abonar a un prestamo anulado.")
    if loan.status == "paid" or loan.balance_amount <= ZERO_MONEY:
        raise ValueError("El prestamo ya esta pagado.")

    amount = payload.amount.quantize(MONEY_QUANTUM)
    if amount > loan.balance_amount:
        raise ValueError(
            "El monto del abono no puede ser mayor al saldo pendiente.",
        )

    payment = control_repository.create_loan_payment(
        db,
        {
            **payload.model_dump(),
            "payment_number": f"PENDING-{uuid4().hex}",
            "employee_loan_id": loan.id,
            "employee_id": loan.employee_id,
            "amount": amount,
            "status": "active",
            "created_by": created_by,
        },
    )
    loan.paid_amount = (loan.paid_amount + amount).quantize(MONEY_QUANTUM)
    loan.balance_amount = (loan.balance_amount - amount).quantize(MONEY_QUANTUM)
    loan.status = "paid" if loan.balance_amount == ZERO_MONEY else "active"
    db.add(loan)
    try:
        db.flush()
        payment.payment_number = (
            f"ELP-{payment.payment_date:%Y%m%d}-{payment.id:04d}"
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar el abono al prestamo.") from error
    return _require_loan_payment(db, payment.id)


def list_loan_payments(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    loan_id: int | None = None,
    status: str | None = None,
) -> list[EmployeeLoanPayment]:
    _validate_date_range(date_from, date_to)
    return control_repository.list_loan_payments(
        db=db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
        loan_id=loan_id,
        status=status,
    )


def void_loan_payment(
    db: Session,
    payment_id: int,
    reason: str,
) -> EmployeeLoanPayment:
    existing_payment = control_repository.get_loan_payment(db, payment_id)
    if existing_payment is None:
        raise ValueError("El abono al prestamo no existe.")
    loan = control_repository.get_loan(
        db,
        existing_payment.employee_loan_id,
        for_update=True,
    )
    if loan is None:
        raise ValueError("El prestamo no existe.")
    payment = control_repository.get_loan_payment(
        db,
        payment_id,
        for_update=True,
    )
    if payment is None:
        raise ValueError("El abono al prestamo no existe.")
    if payment.status == "voided":
        raise ValueError("El abono al prestamo ya esta anulado.")
    if loan.status == "voided":
        raise ValueError("No se puede modificar un prestamo anulado.")
    if payment.amount > loan.paid_amount:
        raise RuntimeError(
            "El abono no coincide con el monto pagado del prestamo.",
        )

    loan.paid_amount = (loan.paid_amount - payment.amount).quantize(MONEY_QUANTUM)
    loan.balance_amount = (loan.balance_amount + payment.amount).quantize(
        MONEY_QUANTUM,
    )
    loan.status = "active"
    db.add(loan)
    control_repository.mark_loan_payment_voided(
        db,
        payment,
        reason,
        datetime.now(timezone.utc),
    )
    _commit(db, "No se pudo anular el abono al prestamo.")
    return _require_loan_payment(db, payment.id)


def get_account_summary(
    db: Session,
    employee_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict[str, object]:
    _validate_date_range(date_from, date_to)
    employee = employee_repository.get_employee(db, employee_id)
    if employee is None:
        raise ValueError("El empleado no existe.")

    attendance = control_repository.list_attendance(
        db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
    )
    advances = control_repository.list_advances(
        db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
    )
    loans = control_repository.list_loans(
        db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
    )
    payments = control_repository.list_loan_payments(
        db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
    )
    active_advances = [item for item in advances if item.status == "active"]
    valid_loans = [item for item in loans if item.status != "voided"]

    return {
        "employee_id": employee.id,
        "employee_name": _employee_name(employee),
        "advances_total_active": sum(
            (item.amount for item in active_advances),
            start=ZERO_MONEY,
        ),
        "loans_principal_total": sum(
            (item.principal_amount for item in valid_loans),
            start=ZERO_MONEY,
        ),
        "loans_paid_total": sum(
            (item.paid_amount for item in valid_loans),
            start=ZERO_MONEY,
        ),
        "loans_balance_total": sum(
            (item.balance_amount for item in valid_loans),
            start=ZERO_MONEY,
        ),
        "active_loans_count": sum(
            item.status == "active" for item in valid_loans
        ),
        "paid_loans_count": sum(item.status == "paid" for item in valid_loans),
        "attendance_count_period": len(attendance),
        "latest_advances": advances[:5],
        "latest_loans": loans[:5],
        "latest_loan_payments": payments[:5],
    }


def _get_active_employee(db: Session, employee_id: int) -> Employee:
    employee = employee_repository.get_employee(db, employee_id)
    if employee is None:
        raise ValueError("El empleado no existe.")
    if not employee.is_active:
        raise ValueError("El empleado esta inactivo.")
    return employee


def _ensure_attendance_is_available(
    db: Session,
    employee_id: int,
    attendance_date: date,
    *,
    exclude_attendance_id: int | None = None,
) -> None:
    existing = control_repository.get_attendance_by_employee_date(
        db,
        employee_id,
        attendance_date,
        exclude_attendance_id=exclude_attendance_id,
    )
    if existing is not None:
        raise ValueError(
            "Ya existe asistencia para el empleado en la fecha indicada.",
        )


def _require_attendance(
    db: Session,
    attendance_id: int,
) -> EmployeeAttendance:
    attendance = control_repository.get_attendance(db, attendance_id)
    if attendance is None:
        raise ValueError("La asistencia no existe.")
    return attendance


def _require_advance(db: Session, advance_id: int) -> EmployeeAdvance:
    advance = control_repository.get_advance(db, advance_id)
    if advance is None:
        raise ValueError("El anticipo no existe.")
    return advance


def _require_loan(db: Session, loan_id: int) -> EmployeeLoan:
    loan = control_repository.get_loan(db, loan_id)
    if loan is None:
        raise ValueError("El prestamo no existe.")
    return loan


def _require_loan_payment(
    db: Session,
    payment_id: int,
) -> EmployeeLoanPayment:
    payment = control_repository.get_loan_payment(db, payment_id)
    if payment is None:
        raise ValueError("El abono al prestamo no existe.")
    return payment


def _commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(message) from error


def _commit_attendance(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "Ya existe asistencia para el empleado en la fecha indicada.",
        ) from error


def _validate_date_range(
    date_from: date | None,
    date_to: date | None,
) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


def _employee_name(employee: Employee) -> str:
    return f"{employee.first_name} {employee.last_name}"
