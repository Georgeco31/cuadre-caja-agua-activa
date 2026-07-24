from datetime import date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.route_cash_receipt import RouteCashReceipt
from app.models.route_closure import RouteClosure


def get_active_receipt_for_closure(
    db: Session,
    route_closure_id: int,
) -> RouteCashReceipt | None:
    return db.scalar(
        select(RouteCashReceipt)
        .options(*_receipt_options())
        .where(
            RouteCashReceipt.route_closure_id == route_closure_id,
            RouteCashReceipt.status == "active",
        ),
    )


def has_active_receipt_for_closure(
    db: Session,
    route_closure_id: int,
) -> bool:
    statement = (
        select(RouteCashReceipt.id)
        .where(
            RouteCashReceipt.route_closure_id == route_closure_id,
            RouteCashReceipt.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def get_route_cash_receipt(
    db: Session,
    receipt_id: int,
    *,
    for_update: bool = False,
) -> RouteCashReceipt | None:
    statement = (
        select(RouteCashReceipt)
        .options(*_receipt_options())
        .where(RouteCashReceipt.id == receipt_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_route_cash_receipts(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    route_id: int | None = None,
    vehicle_id: int | None = None,
    route_closure_id: int | None = None,
    cash_session_id: int | None = None,
    search: str | None = None,
) -> list[RouteCashReceipt]:
    statement = select(RouteCashReceipt).options(*_receipt_options())
    if date_from is not None:
        statement = statement.where(RouteCashReceipt.receipt_date >= date_from)
    if date_to is not None:
        statement = statement.where(RouteCashReceipt.receipt_date <= date_to)
    if status is not None:
        statement = statement.where(RouteCashReceipt.status == status)
    if route_id is not None:
        statement = statement.where(RouteCashReceipt.route_id == route_id)
    if vehicle_id is not None:
        statement = statement.where(RouteCashReceipt.vehicle_id == vehicle_id)
    if route_closure_id is not None:
        statement = statement.where(
            RouteCashReceipt.route_closure_id == route_closure_id,
        )
    if cash_session_id is not None:
        statement = statement.where(
            RouteCashReceipt.cash_session_id == cash_session_id,
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                RouteCashReceipt.receipt_number.ilike(search_pattern),
                RouteCashReceipt.closure_number_snapshot.ilike(search_pattern),
                RouteCashReceipt.route_name_snapshot.ilike(search_pattern),
                RouteCashReceipt.vehicle_name_snapshot.ilike(search_pattern),
                RouteCashReceipt.notes.ilike(search_pattern),
            ),
        )
    statement = statement.order_by(
        RouteCashReceipt.receipt_date.desc(),
        RouteCashReceipt.id.desc(),
    )
    return list(db.scalars(statement))


def create_route_cash_receipt(
    db: Session,
    values: dict[str, object],
) -> RouteCashReceipt:
    receipt = RouteCashReceipt(**values)
    db.add(receipt)
    return receipt


def mark_route_cash_receipt_voided(
    db: Session,
    receipt: RouteCashReceipt,
    reason: str,
    voided_at: datetime,
) -> RouteCashReceipt:
    receipt.status = "voided"
    receipt.void_reason = reason
    receipt.voided_at = voided_at
    db.add(receipt)
    return receipt


def _receipt_options():
    return (
        joinedload(RouteCashReceipt.route_closure, innerjoin=True).joinedload(
            RouteClosure.route_load,
            innerjoin=True,
        ),
        joinedload(RouteCashReceipt.cash_session, innerjoin=True),
    )
