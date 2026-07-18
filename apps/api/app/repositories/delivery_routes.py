from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.delivery_route import DeliveryRoute


def get_delivery_route(db: Session, route_id: int) -> DeliveryRoute | None:
    return db.get(DeliveryRoute, route_id)


def get_delivery_route_by_code(
    db: Session,
    code: str,
    exclude_route_id: int | None = None,
) -> DeliveryRoute | None:
    statement = select(DeliveryRoute).where(DeliveryRoute.code == code)
    if exclude_route_id is not None:
        statement = statement.where(DeliveryRoute.id != exclude_route_id)
    return db.scalar(statement)


def list_delivery_routes(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    zone: str | None = None,
    sector: str | None = None,
) -> list[DeliveryRoute]:
    statement = select(DeliveryRoute)

    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                DeliveryRoute.name.ilike(search_pattern),
                DeliveryRoute.code.ilike(search_pattern),
                DeliveryRoute.zone.ilike(search_pattern),
                DeliveryRoute.sector.ilike(search_pattern),
                DeliveryRoute.service_days.ilike(search_pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(DeliveryRoute.is_active == is_active)
    if zone is not None:
        statement = statement.where(DeliveryRoute.zone.ilike(zone))
    if sector is not None:
        statement = statement.where(DeliveryRoute.sector.ilike(sector))

    statement = statement.order_by(func.lower(DeliveryRoute.name), DeliveryRoute.id)
    return list(db.scalars(statement))


def create_delivery_route(db: Session, values: dict[str, object]) -> DeliveryRoute:
    delivery_route = DeliveryRoute(**values)
    db.add(delivery_route)
    return delivery_route


def update_delivery_route(
    db: Session,
    delivery_route: DeliveryRoute,
    values: dict[str, object],
) -> DeliveryRoute:
    for field_name, value in values.items():
        setattr(delivery_route, field_name, value)
    db.add(delivery_route)
    return delivery_route


def set_delivery_route_active(
    db: Session,
    delivery_route: DeliveryRoute,
    is_active: bool,
) -> DeliveryRoute:
    delivery_route.is_active = is_active
    db.add(delivery_route)
    return delivery_route
