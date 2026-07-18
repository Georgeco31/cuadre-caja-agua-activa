from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.customer import Customer


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.get(Customer, customer_id)


def get_customer_by_primary_phone(
    db: Session,
    primary_phone: str,
    exclude_customer_id: int | None = None,
) -> Customer | None:
    statement = select(Customer).where(Customer.primary_phone == primary_phone)
    if exclude_customer_id is not None:
        statement = statement.where(Customer.id != exclude_customer_id)
    return db.scalar(statement)


def list_customers(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    customer_type: str | None = None,
    sector: str | None = None,
) -> list[Customer]:
    statement = select(Customer)

    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.primary_phone.ilike(search_pattern),
                Customer.secondary_phone.ilike(search_pattern),
                Customer.sector.ilike(search_pattern),
                Customer.customer_type.ilike(search_pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(Customer.is_active == is_active)
    if customer_type is not None:
        statement = statement.where(Customer.customer_type == customer_type)
    if sector is not None:
        statement = statement.where(func.lower(Customer.sector) == sector.lower())

    statement = statement.order_by(func.lower(Customer.name), Customer.id)
    return list(db.scalars(statement))


def create_customer(db: Session, values: dict[str, object]) -> Customer:
    customer = Customer(**values)
    db.add(customer)
    return customer


def update_customer(
    db: Session,
    customer: Customer,
    values: dict[str, object],
) -> Customer:
    for field_name, value in values.items():
        setattr(customer, field_name, value)
    db.add(customer)
    return customer


def set_customer_active(
    db: Session,
    customer: Customer,
    is_active: bool,
) -> Customer:
    customer.is_active = is_active
    db.add(customer)
    return customer
