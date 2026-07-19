from datetime import date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.delivery_route import DeliveryRoute
from app.models.route_load import RouteLoad
from app.models.route_load_item import RouteLoadItem
from app.models.vehicle import Vehicle


def get_delivery_route_for_update(
    db: Session,
    route_id: int,
) -> DeliveryRoute | None:
    return db.scalar(
        select(DeliveryRoute)
        .where(DeliveryRoute.id == route_id)
        .with_for_update(),
    )


def get_vehicle_for_update(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.scalar(
        select(Vehicle).where(Vehicle.id == vehicle_id).with_for_update(),
    )


def get_route_load(db: Session, load_id: int) -> RouteLoad | None:
    return db.scalar(
        select(RouteLoad).options(*_load_options()).where(RouteLoad.id == load_id),
    )


def get_route_load_for_update(db: Session, load_id: int) -> RouteLoad | None:
    return db.scalar(
        select(RouteLoad)
        .options(*_load_options())
        .where(RouteLoad.id == load_id)
        .with_for_update(),
    )


def list_route_loads(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    route_id: int | None = None,
    vehicle_id: int | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[RouteLoad]:
    statement = select(RouteLoad).options(*_load_options())
    if date_from is not None:
        statement = statement.where(RouteLoad.load_date >= date_from)
    if date_to is not None:
        statement = statement.where(RouteLoad.load_date <= date_to)
    if status is not None:
        statement = statement.where(RouteLoad.status == status)
    if route_id is not None:
        statement = statement.where(RouteLoad.route_id == route_id)
    if vehicle_id is not None:
        statement = statement.where(RouteLoad.vehicle_id == vehicle_id)
    if product_id is not None:
        statement = statement.where(
            RouteLoad.items.any(RouteLoadItem.product_id == product_id),
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                RouteLoad.load_number.ilike(search_pattern),
                RouteLoad.delivery_route.has(DeliveryRoute.name.ilike(search_pattern)),
                RouteLoad.vehicle.has(Vehicle.name.ilike(search_pattern)),
                RouteLoad.items.any(
                    or_(
                        RouteLoadItem.product_name_snapshot.ilike(search_pattern),
                        RouteLoadItem.product_sku_snapshot.ilike(search_pattern),
                    ),
                ),
            ),
        )
    statement = statement.order_by(RouteLoad.load_date.desc(), RouteLoad.id.desc())
    return list(db.scalars(statement))


def has_active_load_for_movement(
    db: Session,
    movement_id: int,
) -> bool:
    statement = (
        select(RouteLoadItem.id)
        .join(RouteLoad)
        .where(
            or_(
                RouteLoadItem.source_exit_movement_id == movement_id,
                RouteLoadItem.destination_entry_movement_id == movement_id,
            ),
            RouteLoad.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def create_route_load(db: Session, values: dict[str, object]) -> RouteLoad:
    route_load = RouteLoad(**values)
    db.add(route_load)
    return route_load


def create_route_load_item(
    db: Session,
    values: dict[str, object],
) -> RouteLoadItem:
    item = RouteLoadItem(**values)
    db.add(item)
    return item


def mark_route_load_voided(
    db: Session,
    route_load: RouteLoad,
    reason: str,
    voided_at: datetime,
) -> RouteLoad:
    route_load.status = "voided"
    route_load.void_reason = reason
    route_load.voided_at = voided_at
    db.add(route_load)
    return route_load


def _load_options():
    return (
        joinedload(RouteLoad.delivery_route, innerjoin=True),
        joinedload(RouteLoad.vehicle, innerjoin=True),
        joinedload(RouteLoad.source_location, innerjoin=True),
        joinedload(RouteLoad.destination_location, innerjoin=True),
        selectinload(RouteLoad.items).joinedload(
            RouteLoadItem.source_exit_movement,
            innerjoin=True,
        ),
        selectinload(RouteLoad.items).joinedload(
            RouteLoadItem.destination_entry_movement,
            innerjoin=True,
        ),
    )
