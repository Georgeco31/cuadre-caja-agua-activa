from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.delivery_route import DeliveryRoute
from app.repositories import delivery_routes
from app.schemas.delivery_route import DeliveryRouteCreate, DeliveryRouteUpdate


def create_delivery_route(
    db: Session,
    payload: DeliveryRouteCreate,
) -> DeliveryRoute:
    if payload.code is not None:
        _ensure_code_is_available(db, payload.code)

    delivery_route = delivery_routes.create_delivery_route(db, payload.model_dump())
    _commit_delivery_route(db, delivery_route)
    return delivery_route


def list_delivery_routes(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    zone: str | None = None,
    sector: str | None = None,
) -> list[DeliveryRoute]:
    return delivery_routes.list_delivery_routes(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        zone=_normalize_filter(zone),
        sector=_normalize_filter(sector),
    )


def get_delivery_route(db: Session, route_id: int) -> DeliveryRoute:
    delivery_route = delivery_routes.get_delivery_route(db, route_id)
    if delivery_route is None:
        raise ValueError("La ruta no existe.")
    return delivery_route


def update_delivery_route(
    db: Session,
    route_id: int,
    payload: DeliveryRouteUpdate,
) -> DeliveryRoute:
    delivery_route = get_delivery_route(db, route_id)
    values = payload.model_dump(exclude_unset=True)

    if "code" in values and values["code"] is not None:
        _ensure_code_is_available(
            db,
            str(values["code"]),
            exclude_route_id=delivery_route.id,
        )

    delivery_routes.update_delivery_route(db, delivery_route, values)
    _commit_delivery_route(db, delivery_route)
    return delivery_route


def deactivate_delivery_route(db: Session, route_id: int) -> DeliveryRoute:
    delivery_route = get_delivery_route(db, route_id)
    delivery_routes.set_delivery_route_active(db, delivery_route, False)
    _commit_delivery_route(db, delivery_route)
    return delivery_route


def activate_delivery_route(db: Session, route_id: int) -> DeliveryRoute:
    delivery_route = get_delivery_route(db, route_id)
    delivery_routes.set_delivery_route_active(db, delivery_route, True)
    _commit_delivery_route(db, delivery_route)
    return delivery_route


def _ensure_code_is_available(
    db: Session,
    code: str,
    exclude_route_id: int | None = None,
) -> None:
    existing_route = delivery_routes.get_delivery_route_by_code(
        db,
        code,
        exclude_route_id=exclude_route_id,
    )
    if existing_route is not None:
        raise ValueError("El codigo de ruta ya esta registrado.")


def _commit_delivery_route(db: Session, delivery_route: DeliveryRoute) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("El codigo de ruta ya esta registrado.") from error
    db.refresh(delivery_route)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
