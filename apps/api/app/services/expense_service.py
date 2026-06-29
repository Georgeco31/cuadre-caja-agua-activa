from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.repositories import cash_sessions, expenses
from app.services.cash_session_service import ensure_cash_session_is_open

MONEY_QUANT = Decimal("0.01")


def create_expense(
    db: Session,
    cash_session_id: int,
    description: str,
    amount: Decimal | str | int,
    category: str | None = None,
    expense_date: date | None = None,
    notes: str | None = None,
) -> Expense:
    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre no existe.")
    ensure_cash_session_is_open(cash_session)

    decimal_amount = _to_money_decimal(amount)
    if decimal_amount <= 0:
        raise ValueError("El monto del gasto debe ser mayor a cero.")

    expense = expenses.create_expense(
        db=db,
        cash_session_id=cash_session_id,
        description=description,
        amount=decimal_amount,
        category=category,
        expense_date=expense_date or cash_session.session_date,
        notes=notes,
    )
    db.commit()
    db.refresh(expense)
    return expense


def _to_money_decimal(amount: Decimal | str | int) -> Decimal:
    if isinstance(amount, float):
        raise ValueError("No usar float para valores monetarios.")
    return Decimal(amount).quantize(MONEY_QUANT)
