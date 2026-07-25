from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.payroll import (
    EmployeePayrollSummary,
    PayrollPreviewRead,
    PayrollPreviewRequest,
    PayrollRunCreate,
    PayrollRunRead,
    PayrollRunSummaryRead,
    PayrollStatus,
    PayrollVoid,
)
from app.services import payroll as payroll_service

router = APIRouter(
    prefix="/payroll",
    tags=["payroll"],
    dependencies=[Depends(get_current_user)],
)
employee_router = APIRouter(
    prefix="/employees",
    tags=["payroll"],
    dependencies=[Depends(get_current_user)],
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


@router.post("/runs/{payroll_run_id}/void", response_model=PayrollRunRead)
def void_payroll_run(
    payroll_run_id: int,
    payload: PayrollVoid,
    db: Session = Depends(get_db),
):
    try:
        return payroll_service.void_run(db, payroll_run_id, payload.reason)
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
        "ya esta" in detail
        or "ya fue usado" in detail
        or "esta anulado" in detail
        or "esta pagado" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
