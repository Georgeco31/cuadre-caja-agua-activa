from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.repositories import inventory
from app.schemas.inventory import (
    InventoryLocationCreate,
    InventoryLocationUpdate,
    InventoryMovementCreate,
)

QUANTITY_QUANTUM = Decimal("0.001")
MONEY_QUANTUM = Decimal("0.01")
INCREASING_MOVEMENT_TYPES = {"entry", "adjustment_in"}


def create_location(
    db: Session,
    payload: InventoryLocationCreate,
) -> InventoryLocation:
    if payload.code is not None:
        _ensure_location_code_available(db, payload.code)
    _ensure_vehicle_exists(db, payload.vehicle_id)
    location = inventory.create_location(db, payload.model_dump())
    _commit_location(db, location)
    return location


def list_locations(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    location_type: str | None = None,
) -> list[InventoryLocation]:
    return inventory.list_locations(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        location_type=location_type,
    )


def get_location(db: Session, location_id: int) -> InventoryLocation:
    location = inventory.get_location(db, location_id)
    if location is None:
        raise ValueError("La ubicacion de inventario no existe.")
    return location


def update_location(
    db: Session,
    location_id: int,
    payload: InventoryLocationUpdate,
) -> InventoryLocation:
    location = get_location(db, location_id)
    values = payload.model_dump(exclude_unset=True)
    if "code" in values and values["code"] is not None:
        _ensure_location_code_available(
            db,
            str(values["code"]),
            exclude_location_id=location.id,
        )
    if "vehicle_id" in values:
        vehicle_id = values["vehicle_id"]
        _ensure_vehicle_exists(
            db,
            int(vehicle_id) if vehicle_id is not None else None,
        )
    inventory.update_location(db, location, values)
    _commit_location(db, location)
    return location


def deactivate_location(db: Session, location_id: int) -> InventoryLocation:
    location = get_location(db, location_id)
    inventory.set_location_active(db, location, False)
    _commit_location(db, location)
    return location


def activate_location(db: Session, location_id: int) -> InventoryLocation:
    location = get_location(db, location_id)
    inventory.set_location_active(db, location, True)
    _commit_location(db, location)
    return location


def list_stocks(
    db: Session,
    product_id: int | None = None,
    location_id: int | None = None,
    only_positive: bool = False,
) -> list[InventoryStock]:
    return inventory.list_stocks(
        db=db,
        product_id=product_id,
        location_id=location_id,
        only_positive=only_positive,
    )


def create_movement(
    db: Session,
    payload: InventoryMovementCreate,
    created_by: int,
) -> InventoryMovement:
    product = inventory.get_product(db, payload.product_id, for_update=True)
    if product is None:
        raise ValueError("El producto no existe.")
    if not product.is_active:
        raise ValueError("No se puede mover inventario de un producto inactivo.")

    location = inventory.get_location(db, payload.location_id, for_update=True)
    if location is None:
        raise ValueError("La ubicacion de inventario no existe.")
    if not location.is_active:
        raise ValueError("No se puede mover inventario en una ubicacion inactiva.")

    quantity = payload.quantity.quantize(QUANTITY_QUANTUM)
    stock = inventory.get_stock(
        db,
        product.id,
        location.id,
        for_update=True,
    )
    current_quantity = (
        stock.quantity_on_hand if stock is not None else Decimal("0.000")
    )
    increases_stock = payload.movement_type in INCREASING_MOVEMENT_TYPES
    if not increases_stock and quantity > current_quantity:
        raise ValueError("No hay stock suficiente para registrar el movimiento.")

    if stock is None:
        stock = inventory.create_stock(
            db,
            {
                "product_id": product.id,
                "location_id": location.id,
                "quantity_on_hand": Decimal("0.000"),
            },
        )

    stock.quantity_on_hand = (
        current_quantity + quantity
        if increases_stock
        else current_quantity - quantity
    ).quantize(QUANTITY_QUANTUM)
    db.add(stock)

    unit_cost = (
        payload.unit_cost.quantize(MONEY_QUANTUM)
        if payload.unit_cost is not None
        else None
    )
    total_cost = (
        (quantity * unit_cost).quantize(MONEY_QUANTUM)
        if unit_cost is not None
        else None
    )
    movement = inventory.create_movement(
        db,
        {
            "movement_date": payload.movement_date,
            "movement_type": payload.movement_type,
            "product_id": product.id,
            "location_id": location.id,
            "product_sku_snapshot": product.sku,
            "product_name_snapshot": product.name,
            "product_presentation_snapshot": product.presentation,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "total_cost": total_cost,
            "reason": payload.reason,
            "status": "active",
            "created_by": created_by,
        },
    )
    _commit_movement(db, movement, "No se pudo registrar el movimiento.")
    return _get_movement_after_commit(db, movement.id)


def list_movements(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    product_id: int | None = None,
    location_id: int | None = None,
    movement_type: str | None = None,
    status: str | None = None,
) -> list[InventoryMovement]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return inventory.list_movements(
        db=db,
        date_from=date_from,
        date_to=date_to,
        product_id=product_id,
        location_id=location_id,
        movement_type=movement_type,
        status=status,
    )


def get_movement(db: Session, movement_id: int) -> InventoryMovement:
    movement = inventory.get_movement(db, movement_id)
    if movement is None:
        raise ValueError("El movimiento de inventario no existe.")
    return movement


def void_movement(
    db: Session,
    movement_id: int,
    reason: str,
) -> InventoryMovement:
    movement = inventory.get_movement(db, movement_id, for_update=True)
    if movement is None:
        raise ValueError("El movimiento de inventario no existe.")
    if movement.status == "voided":
        raise ValueError("El movimiento de inventario ya esta anulado.")

    product = inventory.get_product(db, movement.product_id, for_update=True)
    location = inventory.get_location(db, movement.location_id, for_update=True)
    if product is None or location is None:
        raise RuntimeError("El movimiento tiene referencias de inventario invalidas.")
    stock = inventory.get_stock(
        db,
        movement.product_id,
        movement.location_id,
        for_update=True,
    )
    if stock is None:
        raise RuntimeError("El stock del movimiento no existe.")

    if movement.movement_type in INCREASING_MOVEMENT_TYPES:
        if movement.quantity > stock.quantity_on_hand:
            raise ValueError(
                "No se puede anular porque el stock actual es insuficiente."
            )
        stock.quantity_on_hand = (
            stock.quantity_on_hand - movement.quantity
        ).quantize(QUANTITY_QUANTUM)
    else:
        stock.quantity_on_hand = (
            stock.quantity_on_hand + movement.quantity
        ).quantize(QUANTITY_QUANTUM)
    db.add(stock)
    inventory.mark_movement_voided(
        db,
        movement,
        reason,
        datetime.now(timezone.utc),
    )
    _commit_movement(db, movement, "No se pudo anular el movimiento.")
    return _get_movement_after_commit(db, movement.id)


def _ensure_location_code_available(
    db: Session,
    code: str,
    exclude_location_id: int | None = None,
) -> None:
    existing_location = inventory.get_location_by_code(
        db,
        code,
        exclude_location_id=exclude_location_id,
    )
    if existing_location is not None:
        raise ValueError("El codigo de ubicacion ya esta registrado.")


def _ensure_vehicle_exists(db: Session, vehicle_id: int | None) -> None:
    if vehicle_id is not None and inventory.get_vehicle(db, vehicle_id) is None:
        raise ValueError("El vehiculo no existe.")


def _commit_location(db: Session, location: InventoryLocation) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("El codigo de ubicacion ya esta registrado.") from error
    db.refresh(location)


def _commit_movement(
    db: Session,
    movement: InventoryMovement,
    error_message: str,
) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(error_message) from error


def _get_movement_after_commit(
    db: Session,
    movement_id: int,
) -> InventoryMovement:
    movement = inventory.get_movement(db, movement_id)
    if movement is None:
        raise RuntimeError("El movimiento guardado no pudo recuperarse.")
    return movement


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

