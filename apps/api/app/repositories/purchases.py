from datetime import date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.supplier import Supplier


def get_purchase(
    db: Session,
    purchase_id: int,
    *,
    for_update: bool = False,
) -> Purchase | None:
    statement = (
        select(Purchase)
        .options(*_purchase_options())
        .where(Purchase.id == purchase_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_purchases(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    payment_status: str | None = None,
    supplier_id: int | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[Purchase]:
    statement = select(Purchase).join(Purchase.supplier).options(
        *_purchase_options(),
    )
    if date_from is not None:
        statement = statement.where(Purchase.purchase_date >= date_from)
    if date_to is not None:
        statement = statement.where(Purchase.purchase_date <= date_to)
    if status is not None:
        statement = statement.where(Purchase.status == status)
    if payment_status is not None:
        statement = statement.where(Purchase.payment_status == payment_status)
    if supplier_id is not None:
        statement = statement.where(Purchase.supplier_id == supplier_id)
    if product_id is not None:
        statement = statement.where(
            Purchase.items.any(PurchaseItem.product_id == product_id),
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Purchase.purchase_number.ilike(search_pattern),
                Purchase.document_number.ilike(search_pattern),
                Purchase.notes.ilike(search_pattern),
                Supplier.name.ilike(search_pattern),
                Supplier.identification.ilike(search_pattern),
            ),
        )
    statement = statement.order_by(
        Purchase.purchase_date.desc(),
        Purchase.id.desc(),
    )
    return list(db.scalars(statement))


def create_purchase(db: Session, values: dict[str, object]) -> Purchase:
    purchase = Purchase(**values)
    db.add(purchase)
    return purchase


def create_purchase_item(
    db: Session,
    values: dict[str, object],
) -> PurchaseItem:
    item = PurchaseItem(**values)
    db.add(item)
    return item


def mark_purchase_voided(
    db: Session,
    purchase: Purchase,
    reason: str,
    voided_at: datetime,
) -> Purchase:
    purchase.status = "voided"
    purchase.void_reason = reason
    purchase.voided_at = voided_at
    db.add(purchase)
    return purchase


def _purchase_options():
    return (
        joinedload(Purchase.supplier, innerjoin=True),
        selectinload(Purchase.items),
    )
