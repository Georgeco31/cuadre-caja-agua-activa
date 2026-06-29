from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cash_count_item import CashCountItem


def get_count_item(
    db: Session,
    cash_session_id: int,
    denomination_id: int,
) -> CashCountItem | None:
    statement = select(CashCountItem).where(
        CashCountItem.cash_session_id == cash_session_id,
        CashCountItem.denomination_id == denomination_id,
    )
    return db.scalar(statement)


def create_count_item(
    db: Session,
    cash_session_id: int,
    denomination_id: int,
    quantity: int,
    subtotal: Decimal,
) -> CashCountItem:
    count_item = CashCountItem(
        cash_session_id=cash_session_id,
        denomination_id=denomination_id,
        quantity=quantity,
        subtotal=subtotal,
    )
    db.add(count_item)
    return count_item


def update_count_item(
    db: Session,
    count_item: CashCountItem,
    quantity: int,
    subtotal: Decimal,
) -> CashCountItem:
    count_item.quantity = quantity
    count_item.subtotal = subtotal
    db.add(count_item)
    return count_item
