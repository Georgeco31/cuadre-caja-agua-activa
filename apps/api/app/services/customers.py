from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories import customers
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    if payload.primary_phone is not None:
        _ensure_primary_phone_is_available(db, payload.primary_phone)

    customer = customers.create_customer(db, payload.model_dump())
    _commit_customer(db, customer)
    return customer


def list_customers(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    customer_type: str | None = None,
    sector: str | None = None,
) -> list[Customer]:
    return customers.list_customers(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        customer_type=customer_type,
        sector=_normalize_filter(sector),
    )


def get_customer(db: Session, customer_id: int) -> Customer:
    customer = customers.get_customer(db, customer_id)
    if customer is None:
        raise ValueError("El cliente no existe.")
    return customer


def update_customer(
    db: Session,
    customer_id: int,
    payload: CustomerUpdate,
) -> Customer:
    customer = get_customer(db, customer_id)
    values = payload.model_dump(exclude_unset=True)

    if "primary_phone" in values and values["primary_phone"] is not None:
        _ensure_primary_phone_is_available(
            db,
            str(values["primary_phone"]),
            exclude_customer_id=customer.id,
        )

    customers.update_customer(db, customer, values)
    _commit_customer(db, customer)
    return customer


def deactivate_customer(db: Session, customer_id: int) -> Customer:
    customer = get_customer(db, customer_id)
    customers.set_customer_active(db, customer, False)
    _commit_customer(db, customer)
    return customer


def activate_customer(db: Session, customer_id: int) -> Customer:
    customer = get_customer(db, customer_id)
    customers.set_customer_active(db, customer, True)
    _commit_customer(db, customer)
    return customer


def _ensure_primary_phone_is_available(
    db: Session,
    primary_phone: str,
    exclude_customer_id: int | None = None,
) -> None:
    existing_customer = customers.get_customer_by_primary_phone(
        db,
        primary_phone,
        exclude_customer_id=exclude_customer_id,
    )
    if existing_customer is not None:
        raise ValueError("El telefono principal ya esta registrado.")


def _commit_customer(db: Session, customer: Customer) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("El telefono principal ya esta registrado.") from error
    db.refresh(customer)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
