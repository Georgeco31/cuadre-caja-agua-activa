from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.route_closure import RouteClosure
from app.repositories import route_closures as route_closures_repository
from app.repositories import route_loads as route_loads_repository
from app.schemas.route_closure import (
    RouteClosureCreate,
    RouteLoadFinancialClosureRead,
)
from app.services import route_activity as route_activity_service

MONEY_QUANTUM = Decimal("0.01")


def create_route_closure(
    db: Session,
    payload: RouteClosureCreate,
    created_by: int,
) -> RouteClosure:
    route_load = route_loads_repository.get_route_load_for_update(
        db,
        payload.route_load_id,
    )
    if route_load is None:
        raise ValueError("La carga de ruta no existe.")
    if route_load.status != "active":
        raise ValueError("No se puede cerrar financieramente una carga anulada.")
    if route_closures_repository.has_active_closure_for_load(db, route_load.id):
        raise ValueError("La carga ya tiene un cierre financiero activo.")

    activity = route_activity_service.get_commercial_activity(db, route_load.id)
    delivered_cash_total = payload.delivered_cash_total.quantize(MONEY_QUANTUM)
    difference_amount = (
        delivered_cash_total - activity.expected_cash_total
    ).quantize(MONEY_QUANTUM)
    closure = route_closures_repository.create_route_closure(
        db,
        {
            "closure_number": f"PENDING-{uuid4().hex}",
            "closure_date": payload.closure_date,
            "route_load_id": route_load.id,
            "route_id": route_load.route_id,
            "vehicle_id": route_load.vehicle_id,
            "load_number_snapshot": route_load.load_number,
            "route_name_snapshot": route_load.route_name,
            "vehicle_name_snapshot": route_load.vehicle_name,
            "cash_sales_total": activity.cash_sales_total,
            "credit_sales_total": activity.credit_sales_total,
            "payments_total": activity.payments_total,
            "expected_cash_total": activity.expected_cash_total,
            "delivered_cash_total": delivered_cash_total,
            "difference_amount": difference_amount,
            "status": "active",
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        closure.closure_number = (
            f"CLOSE-{closure.closure_date:%Y%m%d}-{closure.id:04d}"
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "No se pudo registrar el cierre financiero. "
            "Verifique que la carga no tenga otro cierre activo.",
        ) from error

    created_closure = route_closures_repository.get_route_closure(db, closure.id)
    if created_closure is None:
        raise RuntimeError("El cierre financiero registrado no pudo recuperarse.")
    return created_closure


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
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return route_closures_repository.list_route_closures(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        route_id=route_id,
        vehicle_id=vehicle_id,
        route_load_id=route_load_id,
        search=_normalize_filter(search),
    )


def get_route_closure(db: Session, closure_id: int) -> RouteClosure:
    closure = route_closures_repository.get_route_closure(db, closure_id)
    if closure is None:
        raise ValueError("El cierre financiero de ruta no existe.")
    return closure


def get_financial_closure_for_load(
    db: Session,
    load_id: int,
) -> RouteLoadFinancialClosureRead:
    route_load = route_loads_repository.get_route_load(db, load_id)
    if route_load is None:
        raise ValueError("La carga de ruta no existe.")
    closure = route_closures_repository.get_active_closure_for_load(db, load_id)
    return RouteLoadFinancialClosureRead(
        status="closed" if closure is not None else "not_closed",
        active_closure=closure,
    )


def void_route_closure(
    db: Session,
    closure_id: int,
    reason: str,
) -> RouteClosure:
    closure = route_closures_repository.get_route_closure(
        db,
        closure_id,
        for_update=True,
    )
    if closure is None:
        raise ValueError("El cierre financiero de ruta no existe.")
    if closure.status == "voided":
        raise ValueError("El cierre financiero de ruta ya esta anulado.")

    route_closures_repository.mark_route_closure_voided(
        db,
        closure,
        reason,
        datetime.now(timezone.utc),
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular el cierre financiero.") from error

    voided_closure = route_closures_repository.get_route_closure(db, closure.id)
    if voided_closure is None:
        raise RuntimeError("El cierre financiero anulado no pudo recuperarse.")
    return voided_closure


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
