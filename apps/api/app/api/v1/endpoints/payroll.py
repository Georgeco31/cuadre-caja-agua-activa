from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import ROLE_ADMIN_AUDITOR, get_current_user, get_db
from app.models.user import User
from app.schemas.payroll import (
    EmployeePayrollSummary,
    PayrollCancel,
    PayrollItemInput,
    PayrollItemUpdate,
    PayrollPreviewRead,
    PayrollPreviewRequest,
    PayrollRunCreate,
    PayrollRunRead,
    PayrollRunSummaryRead,
    PayrollStatus,
)
from app.services import payroll as payroll_service


def _require_payroll_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != ROLE_ADMIN_AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar roles de pago.",
        )
    return current_user


router = APIRouter(
    prefix="/payroll",
    tags=["payroll"],
    dependencies=[Depends(_require_payroll_admin)],
)
employee_router = APIRouter(
    prefix="/employees",
    tags=["payroll"],
    dependencies=[Depends(_require_payroll_admin)],
)


@router.post("/runs/preview", response_model=PayrollPreviewRead)
def preview_payroll_run(
    payload: PayrollPreviewRequest,
    db: Session = Depends(get_db),
):
    try:
        return payroll_service.preview_run(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/runs",
    response_model=PayrollRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_payroll_run(
    payload: PayrollRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payroll_service.create_run(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/runs/{payroll_run_id}/items",
    response_model=PayrollRunRead,
    status_code=status.HTTP_201_CREATED,
)
def add_payroll_item(
    payroll_run_id: int,
    payload: PayrollItemInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payroll_service.add_item(
            db,
            payroll_run_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/items/{payroll_item_id}", response_model=PayrollRunRead)
def update_payroll_item(
    payroll_item_id: int,
    payload: PayrollItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payroll_service.update_item(
            db,
            payroll_item_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/runs", response_model=list[PayrollRunSummaryRead])
def list_payroll_runs(
    date_from: date | None = None,
    date_to: date | None = None,
    payroll_status: PayrollStatus | None = Query(default=None, alias="status"),
    employee_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return payroll_service.list_runs(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=payroll_status,
            employee_id=employee_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/runs/{payroll_run_id}", response_model=PayrollRunRead)
def get_payroll_run(
    payroll_run_id: int,
    db: Session = Depends(get_db),
):
    try:
        return payroll_service.get_run(db, payroll_run_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/runs/{payroll_run_id}/approve",
    response_model=PayrollRunRead,
)
def approve_payroll_run(
    payroll_run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payroll_service.approve_run(
            db,
            payroll_run_id,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/runs/{payroll_run_id}/mark-paid",
    response_model=PayrollRunRead,
)
def mark_payroll_run_paid(
    payroll_run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payroll_service.mark_run_paid(
            db,
            payroll_run_id,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/runs/{payroll_run_id}/cancel",
    response_model=PayrollRunRead,
)
def cancel_payroll_run(
    payroll_run_id: int,
    payload: PayrollCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payroll_service.cancel_run(
            db,
            payroll_run_id,
            payload.reason,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/runs/{payroll_run_id}/void",
    response_model=PayrollRunRead,
    deprecated=True,
)
def cancel_payroll_run_legacy(
    payroll_run_id: int,
    payload: PayrollCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cancel_payroll_run(
        payroll_run_id,
        payload,
        db,
        current_user,
    )


@router.get(
    "/employees/{employee_id}/summary",
    response_model=EmployeePayrollSummary,
)
def get_payroll_employee_summary(
    employee_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return payroll_service.get_employee_payroll_summary(
            db,
            employee_id,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as error:
        raise _http_error(error) from error


@employee_router.get(
    "/{employee_id}/payroll-summary",
    response_model=EmployeePayrollSummary,
)
def get_employee_payroll_summary(
    employee_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return payroll_service.get_employee_payroll_summary(
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
        "ya está" in detail
        or "ya fue" in detail
        or "está anulado" in detail
        or "está pagado" in detail
        or "reservado" in detail
        or "no puede modificarse" in detail
        or "no puede cancelarse" in detail
        or "debe aprobarse" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
