from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.employee import Employee


def get_employee(db: Session, employee_id: int) -> Employee | None:
    return db.get(Employee, employee_id)


def get_employee_by_identification(
    db: Session,
    identification: str,
    exclude_employee_id: int | None = None,
) -> Employee | None:
    statement = select(Employee).where(Employee.identification == identification)
    if exclude_employee_id is not None:
        statement = statement.where(Employee.id != exclude_employee_id)
    return db.scalar(statement)


def list_employees(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    employee_type: str | None = None,
    job_position: str | None = None,
) -> list[Employee]:
    statement = select(Employee)

    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Employee.first_name.ilike(search_pattern),
                Employee.last_name.ilike(search_pattern),
                (Employee.first_name + " " + Employee.last_name).ilike(search_pattern),
                Employee.identification.ilike(search_pattern),
                Employee.primary_phone.ilike(search_pattern),
                Employee.secondary_phone.ilike(search_pattern),
                Employee.job_position.ilike(search_pattern),
                Employee.employee_type.ilike(search_pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(Employee.is_active == is_active)
    if employee_type is not None:
        statement = statement.where(Employee.employee_type == employee_type)
    if job_position is not None:
        statement = statement.where(Employee.job_position.ilike(job_position))

    statement = statement.order_by(
        func.lower(Employee.last_name),
        func.lower(Employee.first_name),
        Employee.id,
    )
    return list(db.scalars(statement))


def create_employee(db: Session, values: dict[str, object]) -> Employee:
    employee = Employee(**values)
    db.add(employee)
    return employee


def update_employee(
    db: Session,
    employee: Employee,
    values: dict[str, object],
) -> Employee:
    for field_name, value in values.items():
        setattr(employee, field_name, value)
    db.add(employee)
    return employee


def deactivate_employee(
    db: Session,
    employee: Employee,
    termination_date: date | None = None,
) -> Employee:
    employee.is_active = False
    if termination_date is not None:
        employee.termination_date = termination_date
    db.add(employee)
    return employee


def activate_employee(db: Session, employee: Employee) -> Employee:
    employee.is_active = True
    employee.termination_date = None
    db.add(employee)
    return employee
