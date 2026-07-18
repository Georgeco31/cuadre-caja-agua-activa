from datetime import date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.sale import Sale
from app.models.sale_item import SaleItem


def get_sale(db: Session, sale_id: int) -> Sale | None:
    statement = (
        select(Sale)
        .options(selectinload(Sale.items))
        .where(Sale.id == sale_id)
    )
    return db.scalar(statement)


def list_sales(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    customer_id: int | None = None,
    payment_method: str | None = None,
    search: str | None = None,
) -> list[Sale]:
    statement = select(Sale).options(selectinload(Sale.items))

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


def create_sale(db: Session, values: dict[str, object]) -> Sale:
    sale = Sale(**values)
    db.add(sale)
    return sale


def create_sale_item(db: Session, values: dict[str, object]) -> SaleItem:
    sale_item = SaleItem(**values)
    db.add(sale_item)
    return sale_item


def mark_sale_voided(
    db: Session,
    sale: Sale,
    reason: str,
    voided_at: datetime,
) -> Sale:
    sale.status = "voided"
    sale.void_reason = reason
    sale.voided_at = voided_at
    db.add(sale)
    return sale
