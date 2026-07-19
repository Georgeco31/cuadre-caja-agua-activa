from datetime import date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.delivery_route import DeliveryRoute
from app.models.route_load import RouteLoad
from app.models.route_return import RouteReturn
from app.models.route_return_item import RouteReturnItem
from app.models.vehicle import Vehicle


def get_active_return_for_load(
    db: Session,
    route_load_id: int,
) -> RouteReturn | None:
    return db.scalar(
        select(RouteReturn).where(
            RouteReturn.route_load_id == route_load_id,
            RouteReturn.status == "active",
        ),
    )


def has_active_return_for_load(db: Session, route_load_id: int) -> bool:
    statement = (
        select(RouteReturn.id)
        .where(
            RouteReturn.route_load_id == route_load_id,
            RouteReturn.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def has_active_return_for_movement(db: Session, movement_id: int) -> bool:
    statement = (
        select(RouteReturnItem.id)
        .join(RouteReturn)
        .where(
            or_(
                RouteReturnItem.source_exit_movement_id == movement_id,
                RouteReturnItem.destination_entry_movement_id == movement_id,
            ),
            RouteReturn.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def get_route_return(db: Session, return_id: int) -> RouteReturn | None:
    return db.scalar(
        select(RouteReturn)
        .options(*_return_options())
        .where(RouteReturn.id == return_id),
    )


def get_route_return_for_update(
    db: Session,
    return_id: int,
) -> RouteReturn | None:
    return db.scalar(
        select(RouteReturn)
        .options(*_return_options())
        .where(RouteReturn.id == return_id)
        .with_for_update(),
    )


def list_route_returns(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    route_id: int | None = None,
    vehicle_id: int | None = None,
    route_load_id: int | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[RouteReturn]:
    statement = select(RouteReturn).options(*_return_options())
    if date_from is not None:
        statement = statement.where(RouteReturn.return_date >= date_from)
    if date_to is not None:
        statement = statement.where(RouteReturn.return_date <= date_to)
    if status is not None:
        statement = statement.where(RouteReturn.status == status)
    if route_id is not None:
        statement = statement.where(RouteReturn.route_id == route_id)
    if vehicle_id is not None:
        statement = statement.where(RouteReturn.vehicle_id == vehicle_id)
    if route_load_id is not None:
        statement = statement.where(RouteReturn.route_load_id == route_load_id)
    if product_id is not None:
        statement = statement.where(
            RouteReturn.items.any(RouteReturnItem.product_id == product_id),
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                RouteReturn.return_number.ilike(search_pattern),
                RouteReturn.route_load.has(
                    RouteLoad.load_number.ilike(search_pattern),
                ),
                RouteReturn.delivery_route.has(
                    DeliveryRoute.name.ilike(search_pattern),
                ),
                RouteReturn.vehicle.has(Vehicle.name.ilike(search_pattern)),
                RouteReturn.items.any(
                    or_(
                        RouteReturnItem.product_name_snapshot.ilike(search_pattern),
                        RouteReturnItem.product_sku_snapshot.ilike(search_pattern),
                    ),
                ),
            ),
        )
    statement = statement.order_by(
        RouteReturn.return_date.desc(),
        RouteReturn.id.desc(),
    )
    return list(db.scalars(statement))


def create_route_return(db: Session, values: dict[str, object]) -> RouteReturn:
    route_return = RouteReturn(**values)
    db.add(route_return)
    return route_return


def create_route_return_item(
    db: Session,
    values: dict[str, object],
) -> RouteReturnItem:
    item = RouteReturnItem(**values)
    db.add(item)
    return item


def mark_route_return_voided(
    db: Session,
    route_return: RouteReturn,
    reason: str,
    voided_at: datetime,
) -> RouteReturn:
    route_return.status = "voided"
    route_return.void_reason = reason
    route_return.voided_at = voided_at
    db.add(route_return)
    return route_return


def _return_options():
    return (
        joinedload(RouteReturn.route_load, innerjoin=True),
        joinedload(RouteReturn.delivery_route, innerjoin=True),
        joinedload(RouteReturn.vehicle, innerjoin=True),
        joinedload(RouteReturn.source_location, innerjoin=True),
        joinedload(RouteReturn.destination_location, innerjoin=True),
        selectinload(RouteReturn.items).joinedload(
            RouteReturnItem.route_load_item,
            innerjoin=True,
        ),
        selectinload(RouteReturn.items).joinedload(
            RouteReturnItem.source_exit_movement,
            innerjoin=True,
        ),
        selectinload(RouteReturn.items).joinedload(
            RouteReturnItem.destination_entry_movement,
            innerjoin=True,
        ),
    )
