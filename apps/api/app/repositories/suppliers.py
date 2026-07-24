from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier


def get_supplier(db: Session, supplier_id: int) -> Supplier | None:
    return db.get(Supplier, supplier_id)


def get_supplier_by_identification(
    db: Session,
    identification: str,
    exclude_supplier_id: int | None = None,
) -> Supplier | None:
    statement = select(Supplier).where(
        Supplier.identification == identification,
    )
    if exclude_supplier_id is not None:
        statement = statement.where(Supplier.id != exclude_supplier_id)
    return db.scalar(statement)


def list_suppliers(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    supplier_type: str | None = None,
) -> list[Supplier]:
    statement = select(Supplier)
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Supplier.name.ilike(search_pattern),
                Supplier.identification.ilike(search_pattern),
                Supplier.primary_phone.ilike(search_pattern),
                Supplier.secondary_phone.ilike(search_pattern),
                Supplier.email.ilike(search_pattern),
                Supplier.contact_name.ilike(search_pattern),
                Supplier.supplier_type.ilike(search_pattern),
            ),
        )
    if is_active is not None:
        statement = statement.where(Supplier.is_active == is_active)
    if supplier_type is not None:
        statement = statement.where(Supplier.supplier_type == supplier_type)
    statement = statement.order_by(func.lower(Supplier.name), Supplier.id)
    return list(db.scalars(statement))


def create_supplier(db: Session, values: dict[str, object]) -> Supplier:
    supplier = Supplier(**values)
    db.add(supplier)
    return supplier


def update_supplier(
    db: Session,
    supplier: Supplier,
    values: dict[str, object],
) -> Supplier:
    for field_name, value in values.items():
        setattr(supplier, field_name, value)
    db.add(supplier)
    return supplier


def set_supplier_active(
    db: Session,
    supplier: Supplier,
    is_active: bool,
) -> Supplier:
    supplier.is_active = is_active
    db.add(supplier)
    return supplier
