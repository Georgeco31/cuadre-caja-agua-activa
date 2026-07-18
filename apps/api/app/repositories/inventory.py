from datetime import date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.product import Product
from app.models.vehicle import Vehicle


def get_location(
    db: Session,
    location_id: int,
    *,
    for_update: bool = False,
) -> InventoryLocation | None:
    statement = select(InventoryLocation).where(
        InventoryLocation.id == location_id
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def get_location_by_code(
    db: Session,
    code: str,
    exclude_location_id: int | None = None,
) -> InventoryLocation | None:
    statement = select(InventoryLocation).where(InventoryLocation.code == code)
    if exclude_location_id is not None:
        statement = statement.where(InventoryLocation.id != exclude_location_id)
    return db.scalar(statement)


def list_locations(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    location_type: str | None = None,
) -> list[InventoryLocation]:
    statement = select(InventoryLocation)
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                InventoryLocation.name.ilike(search_pattern),
                InventoryLocation.code.ilike(search_pattern),
                InventoryLocation.description.ilike(search_pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(InventoryLocation.is_active == is_active)
    if location_type is not None:
        statement = statement.where(
            InventoryLocation.location_type == location_type
        )
    statement = statement.order_by(
        func.lower(InventoryLocation.name),
        InventoryLocation.id,
    )
    return list(db.scalars(statement))


def create_location(
    db: Session,
    values: dict[str, object],
) -> InventoryLocation:
    location = InventoryLocation(**values)
    db.add(location)
    return location


def update_location(
    db: Session,
    location: InventoryLocation,
    values: dict[str, object],
) -> InventoryLocation:
    for field_name, value in values.items():
        setattr(location, field_name, value)
    db.add(location)
    return location


def set_location_active(
    db: Session,
    location: InventoryLocation,
    is_active: bool,
) -> InventoryLocation:
    location.is_active = is_active
    db.add(location)
    return location


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.get(Vehicle, vehicle_id)


def get_product(
    db: Session,
    product_id: int,
    *,
    for_update: bool = False,
) -> Product | None:
    statement = select(Product).where(Product.id == product_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def get_stock(
    db: Session,
    product_id: int,
    location_id: int,
    *,
    for_update: bool = False,
) -> InventoryStock | None:
    statement = select(InventoryStock).where(
        InventoryStock.product_id == product_id,
        InventoryStock.location_id == location_id,
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_stocks(
    db: Session,
    product_id: int | None = None,
    location_id: int | None = None,
    only_positive: bool = False,
) -> list[InventoryStock]:
    statement = select(InventoryStock).options(
        selectinload(InventoryStock.product),
        selectinload(InventoryStock.location),
    )
    if product_id is not None:
        statement = statement.where(InventoryStock.product_id == product_id)
    if location_id is not None:
        statement = statement.where(InventoryStock.location_id == location_id)
    if only_positive:
        statement = statement.where(InventoryStock.quantity_on_hand > 0)
    statement = statement.join(InventoryStock.product).join(
        InventoryStock.location
    )
    statement = statement.order_by(
        func.lower(InventoryLocation.name),
        func.lower(Product.name),
        InventoryStock.id,
    )
    return list(db.scalars(statement))


def create_stock(
    db: Session,
    values: dict[str, object],
) -> InventoryStock:
    stock = InventoryStock(**values)
    db.add(stock)
    return stock


def get_movement(
    db: Session,
    movement_id: int,
    *,
    for_update: bool = False,
) -> InventoryMovement | None:
    statement = (
        select(InventoryMovement)
        .options(selectinload(InventoryMovement.location))
        .where(InventoryMovement.id == movement_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_movements(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    product_id: int | None = None,
    location_id: int | None = None,
    movement_type: str | None = None,
    status: str | None = None,
) -> list[InventoryMovement]:
    statement = select(InventoryMovement).options(
        selectinload(InventoryMovement.location)
    )
    if date_from is not None:
        statement = statement.where(InventoryMovement.movement_date >= date_from)
    if date_to is not None:
        statement = statement.where(InventoryMovement.movement_date <= date_to)
    if product_id is not None:
        statement = statement.where(InventoryMovement.product_id == product_id)
    if location_id is not None:
        statement = statement.where(InventoryMovement.location_id == location_id)
    if movement_type is not None:
        statement = statement.where(
            InventoryMovement.movement_type == movement_type
        )
    if status is not None:
        statement = statement.where(InventoryMovement.status == status)
    statement = statement.order_by(
        InventoryMovement.movement_date.desc(),
        InventoryMovement.id.desc(),
    )
    return list(db.scalars(statement))


def create_movement(
    db: Session,
    values: dict[str, object],
) -> InventoryMovement:
    movement = InventoryMovement(**values)
    db.add(movement)
    return movement


def mark_movement_voided(
    db: Session,
    movement: InventoryMovement,
    reason: str,
    voided_at: datetime,
) -> InventoryMovement:
    movement.status = "voided"
    movement.void_reason = reason
    movement.voided_at = voided_at
    db.add(movement)
    return movement

