from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeDeactivate,
    EmployeeRead,
    EmployeeType,
    EmployeeUpdate,
)
from app.services import employees as employee_service

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
):
    try:
        return employee_service.create_employee(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[EmployeeRead])
def list_employees(
    search: str | None = None,
    is_active: bool | None = None,
    employee_type: EmployeeType | None = None,
    job_position: str | None = None,
    db: Session = Depends(get_db),
):
    return employee_service.list_employees(
        db=db,
        search=search,
        is_active=is_active,
        employee_type=employee_type,
        job_position=job_position,
    )


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        return employee_service.get_employee(db, employee_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    try:
        return employee_service.update_employee(db, employee_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{employee_id}/deactivate", response_model=EmployeeRead)
def deactivate_employee(
    employee_id: int,
    payload: EmployeeDeactivate | None = None,
    db: Session = Depends(get_db),
):
    try:
        return employee_service.deactivate_employee(
            db,
            employee_id,
            payload.termination_date if payload is not None else None,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{employee_id}/activate", response_model=EmployeeRead)
def activate_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        return employee_service.activate_employee(db, employee_id)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta registrada" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
