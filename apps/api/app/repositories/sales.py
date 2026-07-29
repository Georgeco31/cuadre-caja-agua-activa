from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.route_load import RouteLoad


def get_sale(db: Session, sale_id: int) -> Sale | None:
    statement = (
        select(Sale)
        .options(*_sale_options())
        .where(Sale.id == sale_id)
    )
    return db.scalar(statement)


def get_sale_for_update(db: Session, sale_id: int) -> Sale | None:
    statement = (
        select(Sale)
        .options(*_sale_options())
        .where(Sale.id == sale_id)
        .with_for_update(of=Sale)
    )
    return db.scalar(statement)


def list_sales(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    customer_id: int | None = None,
    payment_method: str | None = None,
    sale_type: str | None = None,
    route_load_id: int | None = None,
    search: str | None = None,
) -> list[Sale]:
    statement = select(Sale).options(*_sale_options())

    if date_from is not None:
        statement = statement.where(Sale.sale_date >= date_from)
    if date_to is not None:
        statement = statement.where(Sale.sale_date <= date_to)
    if status is not None:
        statement = statement.where(Sale.status == status)
    if customer_id is not None:
        statement = statement.where(Sale.customer_id == customer_id)
    if payment_method is not None:
        statement = statement.where(Sale.payment_method == payment_method)
    if sale_type is not None:
        statement = statement.where(Sale.sale_type == sale_type)
    if route_load_id is not None:
        statement = statement.where(Sale.route_load_id == route_load_id)
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Sale.sale_number.ilike(search_pattern),
                Sale.customer_name_snapshot.ilike(search_pattern),
            )
        )

    statement = statement.order_by(Sale.sale_date.desc(), Sale.id.desc())
    return list(db.scalars(statement))


def has_active_sales_for_route_load(db: Session, route_load_id: int) -> bool:
    statement = (
        select(Sale.id)
        .where(
            Sale.route_load_id == route_load_id,
            Sale.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def create_sale(db: Session, values: dict[str, object]) -> Sale:
    sale = Sale(**values)
    db.add(sale)
    return sale


def create_sale_item(db: Session, values: dict[str, object]) -> SaleItem:
    sale_item = SaleItem(**values)
    db.add(sale_item)
    return sale_item


def get_customer_for_credit(db: Session, customer_id: int) -> Customer | None:
    statement = (
        select(Customer)
        .where(Customer.id == customer_id)
        .with_for_update()
    )
    return db.scalar(statement)


def get_active_credit_balance(db: Session, customer_id: int) -> Decimal:
    statement = select(
        func.coalesce(func.sum(Sale.balance_amount), Decimal("0.00"))
    ).where(
        Sale.customer_id == customer_id,
        Sale.sale_type == "credit",
        Sale.status == "active",
    )
    return Decimal(db.scalar(statement) or Decimal("0.00"))


def get_credit_balance_totals(
    db: Session,
    customer_id: int,
) -> tuple[Decimal, Decimal, Decimal]:
    statement = select(
        func.coalesce(func.sum(Sale.total_amount), Decimal("0.00")),
        func.coalesce(func.sum(Sale.paid_amount), Decimal("0.00")),
        func.coalesce(func.sum(Sale.balance_amount), Decimal("0.00")),
    ).where(
        Sale.customer_id == customer_id,
        Sale.sale_type == "credit",
        Sale.status == "active",
    )
    row = db.execute(statement).one()
    total_sales, total_paid, total_balance = row
    return (
        Decimal(total_sales),
        Decimal(total_paid),
        Decimal(total_balance),
    )


def has_active_credit_payments(db: Session, sale_id: int) -> bool:
    statement = select(CreditPayment.id).where(
        CreditPayment.sale_id == sale_id,
        CreditPayment.status == "active",
    ).limit(1)
    return db.scalar(statement) is not None


def mark_sale_voided(
    db: Session,
    sale: Sale,
    reason: str,
    voided_at: datetime,
) -> Sale:
    sale.status = "voided"
    sale.void_reason = reason
    sale.voided_at = voided_at
    if sale.sale_type == "credit":
        sale.balance_amount = Decimal("0.00")
        sale.credit_status = "voided"
    db.add(sale)
    return sale


def update_sale_date(
    db: Session,
    sale: Sale,
    new_sale_date: date,
) -> Sale:
    sale.sale_date = new_sale_date
    db.add(sale)
    return sale


def _sale_options():
    return (
        selectinload(Sale.items),
        joinedload(Sale.route_load).joinedload(RouteLoad.delivery_route),
        joinedload(Sale.route_load).joinedload(RouteLoad.vehicle),
    )
