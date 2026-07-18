from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.models.sale import Sale


def get_receivables_summary(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    customer_id: int | None = None,
) -> tuple[int, Decimal, Decimal, Decimal]:
    statement = select(
        func.count(
            func.distinct(
                case(
                    (Sale.balance_amount > 0, Sale.customer_id),
                    else_=None,
                )
            )
        ),
        func.coalesce(func.sum(Sale.total_amount), Decimal("0.00")),
        func.coalesce(func.sum(Sale.paid_amount), Decimal("0.00")),
        func.coalesce(func.sum(Sale.balance_amount), Decimal("0.00")),
    ).where(*_active_credit_conditions(date_from, date_to, customer_id))
    row = db.execute(statement).one()
    return (
        int(row[0]),
        Decimal(row[1]),
        Decimal(row[2]),
        Decimal(row[3]),
    )


def list_receivable_customers(
    db: Session,
    search: str | None = None,
    only_with_balance: bool = False,
    is_active: bool | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    total_balance = func.sum(Sale.balance_amount)
    statement = (
        select(
            Customer.id,
            Customer.name,
            Customer.primary_phone,
            Customer.sector,
            Customer.is_active,
            func.sum(Sale.total_amount),
            func.sum(Sale.paid_amount),
            total_balance,
            func.sum(case((Sale.balance_amount > 0, 1), else_=0)),
        )
        .join(Sale, Sale.customer_id == Customer.id)
        .where(*_active_credit_conditions(date_from, date_to))
    )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.primary_phone.ilike(search_pattern),
                Customer.secondary_phone.ilike(search_pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(Customer.is_active.is_(is_active))

    statement = statement.group_by(
        Customer.id,
        Customer.name,
        Customer.primary_phone,
        Customer.sector,
        Customer.is_active,
    )
    if only_with_balance:
        statement = statement.having(total_balance > 0)
    statement = statement.order_by(total_balance.desc(), Customer.name.asc())
    return list(db.execute(statement).all())


def list_customer_credit_sales(
    db: Session,
    customer_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    include_paid: bool = False,
) -> list[Sale]:
    statement = select(Sale).where(
        *_active_credit_conditions(date_from, date_to, customer_id)
    )
    if not include_paid:
        statement = statement.where(Sale.balance_amount > 0)
    statement = statement.order_by(Sale.sale_date.desc(), Sale.id.desc())
    return list(db.scalars(statement))


def list_customer_payments(
    db: Session,
    customer_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
):
    statement = (
        select(CreditPayment, Sale.sale_number)
        .join(Sale, Sale.id == CreditPayment.sale_id)
        .where(*_active_credit_conditions(date_from, date_to, customer_id))
        .order_by(
            CreditPayment.payment_date.desc(),
            CreditPayment.id.desc(),
        )
    )
    return list(db.execute(statement).all())


def list_overdue_receivables(db: Session, as_of: date):
    statement = (
        select(
            Sale,
            Customer.name,
            Customer.primary_phone,
            Customer.sector,
        )
        .join(Customer, Customer.id == Sale.customer_id)
        .where(
            Sale.sale_type == "credit",
            Sale.status == "active",
            Sale.balance_amount > 0,
            Sale.due_date.is_not(None),
            Sale.due_date < as_of,
        )
        .order_by(Sale.due_date.asc(), Sale.id.asc())
    )
    return list(db.execute(statement).all())


def _active_credit_conditions(
    date_from: date | None,
    date_to: date | None,
    customer_id: int | None = None,
):
    conditions = [
        Sale.sale_type == "credit",
        Sale.status == "active",
    ]
    if date_from is not None:
        conditions.append(Sale.sale_date >= date_from)
    if date_to is not None:
        conditions.append(Sale.sale_date <= date_to)
    if customer_id is not None:
        conditions.append(Sale.customer_id == customer_id)
    return conditions
