from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cash_count_item import CashCountItem
from app.repositories import cash_count_items, cash_sessions, denominations
from app.services.cash_session_service import ensure_cash_session_is_open

MONEY_QUANT = Decimal("0.01")


def set_count_item(
    db: Session,
    cash_session_id: int,
    denomination_id: int,
    quantity: int,
) -> CashCountItem:
    if quantity < 0:
        raise ValueError("La cantidad debe ser mayor o igual a cero.")

    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre no existe.")
    ensure_cash_session_is_open(cash_session)

    denomination = denominations.get_denomination(db, denomination_id)
    if denomination is None:
        raise ValueError("La denominacion no existe.")

    subtotal = _calculate_subtotal(denomination.value, quantity)
    count_item = cash_count_items.get_count_item(
        db=db,
        cash_session_id=cash_session_id,
        denomination_id=denomination_id,
    )

    if count_item is None:
        count_item = cash_count_items.create_count_item(
            db=db,
            cash_session_id=cash_session_id,
            denomination_id=denomination_id,
            quantity=quantity,
            subtotal=subtotal,
        )
    else:
        count_item = cash_count_items.update_count_item(
            db=db,
            count_item=count_item,
            quantity=quantity,
            subtotal=subtotal,
        )

    db.commit()
    db.refresh(count_item)
    return count_item


def _calculate_subtotal(value: Decimal, quantity: int) -> Decimal:
    return (value * Decimal(quantity)).quantize(MONEY_QUANT)
