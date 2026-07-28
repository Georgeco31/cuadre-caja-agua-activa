from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.models.user import User
from app.schemas.employee_controls import (
    AttendanceStatus,
    EmployeeAccountSummary,
    EmployeeAdvanceCreate,
    EmployeeAdvanceRead,
    EmployeeAdvanceStatus,
    EmployeeAttendanceCreate,
    EmployeeAttendanceRead,
    EmployeeAttendanceUpdate,
    EmployeeControlVoid,
    EmployeeLoanCreate,
    EmployeeLoanPaymentCreate,
    EmployeeLoanPaymentRead,
    EmployeeLoanPaymentStatus,
    EmployeeLoanRead,
    EmployeeLoanStatus,
)
from app.services import employee_controls as control_service

router = APIRouter(
    prefix="/employees",
    tags=["employee-controls"],
    dependencies=[Depends(require_admin_auditor)],
)


@router.post(
    "/attendance",
    response_model=EmployeeAttendanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_attendance(
    payload: EmployeeAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return control_service.create_attendance(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/attendance", response_model=list[EmployeeAttendanceRead])
def list_attendance(
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = Query(default=None, gt=0),
    attendance_status: AttendanceStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    try:
        return control_service.list_attendance(
            db=db,
            date_from=date_from,
            date_to=date_to,
            employee_id=employee_id,
            status=attendance_status,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/attendance/{attendance_id}",
    response_model=EmployeeAttendanceRead,
)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
):
    try:
        return control_service.get_attendance(db, attendance_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/attendance/{attendance_id}",
    response_model=EmployeeAttendanceRead,
)
def update_attendance(
    attendance_id: int,
    payload: EmployeeAttendanceUpdate,
    db: Session = Depends(get_db),
):
    try:
        return control_service.update_attendance(db, attendance_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/advances",
    response_model=EmployeeAdvanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_advance(
    payload: EmployeeAdvanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return control_service.create_advance(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/advances", response_model=list[EmployeeAdvanceRead])
def list_advances(
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = Query(default=None, gt=0),
    advance_status: EmployeeAdvanceStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    try:
        return control_service.list_advances(
            db=db,
            date_from=date_from,
            date_to=date_to,
            employee_id=employee_id,
            status=advance_status,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/advances/{advance_id}", response_model=EmployeeAdvanceRead)
def get_advance(advance_id: int, db: Session = Depends(get_db)):
    try:
        return control_service.get_advance(db, advance_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/advances/{advance_id}/void",
    response_model=EmployeeAdvanceRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_advance(
    advance_id: int,
    payload: EmployeeControlVoid,
    db: Session = Depends(get_db),
):
    try:
        return control_service.void_advance(db, advance_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/loans",
    response_model=EmployeeLoanRead,
    status_code=status.HTTP_201_CREATED,
)
def create_loan(
    payload: EmployeeLoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return control_service.create_loan(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/loans", response_model=list[EmployeeLoanRead])
def list_loans(
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = Query(default=None, gt=0),
    loan_status: EmployeeLoanStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    try:
        return control_service.list_loans(
            db=db,
            date_from=date_from,
            date_to=date_to,
            employee_id=employee_id,
            status=loan_status,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/loans/{loan_id}", response_model=EmployeeLoanRead)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        return control_service.get_loan(db, loan_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/loans/{loan_id}/void",
    response_model=EmployeeLoanRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_loan(
    loan_id: int,
    payload: EmployeeControlVoid,
    db: Session = Depends(get_db),
):
    try:
        return control_service.void_loan(db, loan_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/loans/{loan_id}/payments",
    response_model=EmployeeLoanPaymentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_payment(
    loan_id: int,
    payload: EmployeeLoanPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return control_service.create_loan_payment(
            db,
            loan_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/loan-payments",
    response_model=list[EmployeeLoanPaymentRead],
)
def list_loan_payments(
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = Query(default=None, gt=0),
    loan_id: int | None = Query(default=None, gt=0),
    payment_status: EmployeeLoanPaymentStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    try:
        return control_service.list_loan_payments(
            db=db,
            date_from=date_from,
            date_to=date_to,
            employee_id=employee_id,
            loan_id=loan_id,
            status=payment_status,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/loan-payments/{payment_id}/void",
    response_model=EmployeeLoanPaymentRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_loan_payment(
    payment_id: int,
    payload: EmployeeControlVoid,
    db: Session = Depends(get_db),
):
    try:
        return control_service.void_loan_payment(
            db,
            payment_id,
            payload.reason,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/{employee_id}/account-summary",
    response_model=EmployeeAccountSummary,
)
def get_account_summary(
    employee_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return control_service.get_account_summary(
            db,
            employee_id,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if (
        "Ya existe" in detail
        or "ya esta" in detail
        or "pagos activos" in detail
        or "prestamo anulado" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
