from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories import employees
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, payload: EmployeeCreate) -> Employee:
    if payload.identification is not None:
        _ensure_identification_is_available(db, payload.identification)

    employee = employees.create_employee(db, payload.model_dump())
    _commit_employee(db, employee)
    return employee


def list_employees(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    employee_type: str | None = None,
    job_position: str | None = None,
) -> list[Employee]:
    return employees.list_employees(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        employee_type=employee_type,
        job_position=_normalize_filter(job_position),
    )


def get_employee(db: Session, employee_id: int) -> Employee:
    employee = employees.get_employee(db, employee_id)
    if employee is None:
        raise ValueError("El empleado no existe.")
    return employee


def update_employee(
    db: Session,
    employee_id: int,
    payload: EmployeeUpdate,
) -> Employee:
    employee = get_employee(db, employee_id)
    values = payload.model_dump(exclude_unset=True)

    if "identification" in values and values["identification"] is not None:
        _ensure_identification_is_available(
            db,
            str(values["identification"]),
            exclude_employee_id=employee.id,
        )

    employees.update_employee(db, employee, values)
    _commit_employee(db, employee)
    return employee


def deactivate_employee(
    db: Session,
    employee_id: int,
    termination_date: date | None = None,
) -> Employee:
    employee = get_employee(db, employee_id)
    employees.deactivate_employee(db, employee, termination_date)
    _commit_employee(db, employee)
    return employee


def activate_employee(db: Session, employee_id: int) -> Employee:
    employee = get_employee(db, employee_id)
    employees.activate_employee(db, employee)
    _commit_employee(db, employee)
    return employee


def _ensure_identification_is_available(
    db: Session,
    identification: str,
    exclude_employee_id: int | None = None,
) -> None:
    existing_employee = employees.get_employee_by_identification(
        db,
        identification,
        exclude_employee_id=exclude_employee_id,
    )
    if existing_employee is not None:
        raise ValueError("La identificacion ya esta registrada.")


def _commit_employee(db: Session, employee: Employee) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("La identificacion ya esta registrada.") from error
    db.refresh(employee)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
