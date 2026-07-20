from datetime import date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.route_closure import RouteClosure


def get_active_closure_for_load(
    db: Session,
    route_load_id: int,
) -> RouteClosure | None:
    return db.scalar(
        select(RouteClosure)
        .options(*_closure_options())
        .where(
            RouteClosure.route_load_id == route_load_id,
            RouteClosure.status == "active",
        ),
    )


def has_active_closure_for_load(db: Session, route_load_id: int) -> bool:
    statement = (
        select(RouteClosure.id)
        .where(
            RouteClosure.route_load_id == route_load_id,
            RouteClosure.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def get_route_closure(
    db: Session,
    closure_id: int,
    *,
    for_update: bool = False,
) -> RouteClosure | None:
    statement = (
        select(RouteClosure)
        .options(*_closure_options())
        .where(RouteClosure.id == closure_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_route_closures(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    route_id: int | None = None,
    vehicle_id: int | None = None,
    route_load_id: int | None = None,
    search: str | None = None,
) -> list[RouteClosure]:
    statement = select(RouteClosure).options(*_closure_options())
    if date_from is not None:
        statement = statement.where(RouteClosure.closure_date >= date_from)
    if date_to is not None:
        statement = statement.where(RouteClosure.closure_date <= date_to)
    if status is not None:
        statement = statement.where(RouteClosure.status == status)
    if route_id is not None:
        statement = statement.where(RouteClosure.route_id == route_id)
    if vehicle_id is not None:
        statement = statement.where(RouteClosure.vehicle_id == vehicle_id)
    if route_load_id is not None:
        statement = statement.where(RouteClosure.route_load_id == route_load_id)
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                RouteClosure.closure_number.ilike(search_pattern),
                RouteClosure.load_number_snapshot.ilike(search_pattern),
                RouteClosure.route_name_snapshot.ilike(search_pattern),
                RouteClosure.vehicle_name_snapshot.ilike(search_pattern),
            ),
        )
    statement = statement.order_by(
        RouteClosure.closure_date.desc(),
        RouteClosure.id.desc(),
    )
    return list(db.scalars(statement))


def create_route_closure(
    db: Session,
    values: dict[str, object],
) -> RouteClosure:
    closure = RouteClosure(**values)
    db.add(closure)
    return closure


def mark_route_closure_voided(
    db: Session,
    closure: RouteClosure,
    reason: str,
    voided_at: datetime,
) -> RouteClosure:
    closure.status = "voided"
    closure.void_reason = reason
    closure.voided_at = voided_at
    db.add(closure)
    return closure


def _closure_options():
    return (joinedload(RouteClosure.route_load, innerjoin=True),)
