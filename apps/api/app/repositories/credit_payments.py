from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.credit_payment import CreditPayment
from app.models.sale import Sale
from app.models.route_load import RouteLoad


def get_sale_for_update(db: Session, sale_id: int) -> Sale | None:
    statement = select(Sale).where(Sale.id == sale_id).with_for_update()
    return db.scalar(statement)


def get_credit_payment(
    db: Session,
    payment_id: int,
    *,
    for_update: bool = False,
) -> CreditPayment | None:
    statement = (
        select(CreditPayment)
        .options(
            selectinload(CreditPayment.sale),
            selectinload(CreditPayment.customer),
            joinedload(CreditPayment.route_load).joinedload(
                RouteLoad.delivery_route,
            ),
            joinedload(CreditPayment.route_load).joinedload(RouteLoad.vehicle),
        )
        .where(CreditPayment.id == payment_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_credit_payments(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    customer_id: int | None = None,
    sale_id: int | None = None,
    status: str | None = None,
    payment_method: str | None = None,
    route_load_id: int | None = None,
) -> list[CreditPayment]:
    statement = select(CreditPayment).options(
        selectinload(CreditPayment.sale),
        selectinload(CreditPayment.customer),
        joinedload(CreditPayment.route_load).joinedload(RouteLoad.delivery_route),
        joinedload(CreditPayment.route_load).joinedload(RouteLoad.vehicle),
    )

    if date_from is not None:
        statement = statement.where(CreditPayment.payment_date >= date_from)
    if date_to is not None:
        statement = statement.where(CreditPayment.payment_date <= date_to)
    if customer_id is not None:
        statement = statement.where(CreditPayment.customer_id == customer_id)
    if sale_id is not None:
        statement = statement.where(CreditPayment.sale_id == sale_id)
    if status is not None:
        statement = statement.where(CreditPayment.status == status)
    if payment_method is not None:
        statement = statement.where(
            CreditPayment.payment_method == payment_method
        )
    if route_load_id is not None:
        statement = statement.where(CreditPayment.route_load_id == route_load_id)

    statement = statement.order_by(
        CreditPayment.payment_date.desc(),
        CreditPayment.id.desc(),
    )
    return list(db.scalars(statement))


def has_active_payments_for_route_load(db: Session, route_load_id: int) -> bool:
    statement = (
        select(CreditPayment.id)
        .where(
            CreditPayment.route_load_id == route_load_id,
            CreditPayment.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def create_credit_payment(
    db: Session,
    values: dict[str, object],
) -> CreditPayment:
    payment = CreditPayment(**values)
    db.add(payment)
    return payment


def mark_credit_payment_voided(
    db: Session,
    payment: CreditPayment,
    reason: str,
    voided_at: datetime,
) -> CreditPayment:
    payment.status = "voided"
    payment.void_reason = reason
    payment.voided_at = voided_at
    db.add(payment)
    return payment
