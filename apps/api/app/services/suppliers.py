from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.repositories import suppliers
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def create_supplier(db: Session, payload: SupplierCreate) -> Supplier:
    if payload.identification is not None:
        _ensure_identification_available(db, payload.identification)
    supplier = suppliers.create_supplier(db, payload.model_dump())
    _commit_supplier(db, supplier)
    return supplier


def list_suppliers(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    supplier_type: str | None = None,
) -> list[Supplier]:
    return suppliers.list_suppliers(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        supplier_type=_normalize_filter(supplier_type),
    )


def get_supplier(db: Session, supplier_id: int) -> Supplier:
    supplier = suppliers.get_supplier(db, supplier_id)
    if supplier is None:
        raise ValueError("El proveedor no existe.")
    return supplier


def update_supplier(
    db: Session,
    supplier_id: int,
    payload: SupplierUpdate,
) -> Supplier:
    supplier = get_supplier(db, supplier_id)
    values = payload.model_dump(exclude_unset=True)
    identification = values.get("identification")
    if identification is not None:
        _ensure_identification_available(
            db,
            str(identification),
            exclude_supplier_id=supplier.id,
        )
    suppliers.update_supplier(db, supplier, values)
    _commit_supplier(db, supplier)
    return supplier


def deactivate_supplier(db: Session, supplier_id: int) -> Supplier:
    supplier = get_supplier(db, supplier_id)
    suppliers.set_supplier_active(db, supplier, False)
    _commit_supplier(db, supplier)
    return supplier


def activate_supplier(db: Session, supplier_id: int) -> Supplier:
    supplier = get_supplier(db, supplier_id)
    suppliers.set_supplier_active(db, supplier, True)
    _commit_supplier(db, supplier)
    return supplier


def _ensure_identification_available(
    db: Session,
    identification: str,
    exclude_supplier_id: int | None = None,
) -> None:
    existing_supplier = suppliers.get_supplier_by_identification(
        db,
        identification,
        exclude_supplier_id=exclude_supplier_id,
    )
    if existing_supplier is not None:
        raise ValueError("La identificacion del proveedor ya esta registrada.")


def _commit_supplier(db: Session, supplier: Supplier) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "La identificacion del proveedor ya esta registrada.",
        ) from error
    db.refresh(supplier)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
