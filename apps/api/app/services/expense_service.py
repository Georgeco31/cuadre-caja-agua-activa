from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.repositories import cash_sessions, expenses
from app.services.cash_session_service import ensure_cash_session_is_open

MONEY_QUANT = Decimal("0.01")
EXPENSE_TIMING_BEFORE_COUNT = "before_count"
EXPENSE_TIMING_AFTER_COUNT = "after_count"
VALID_EXPENSE_TIMINGS = {
    EXPENSE_TIMING_BEFORE_COUNT,
    EXPENSE_TIMING_AFTER_COUNT,
}


def create_expense(
    db: Session,
    cash_session_id: int,
    description: str,
    amount: Decimal | str | int,
    category: str | None = None,
    expense_timing: str = EXPENSE_TIMING_AFTER_COUNT,
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
    normalized_expense_timing = _normalize_expense_timing(expense_timing)

    expense = expenses.create_expense(
        db=db,
        cash_session_id=cash_session_id,
        description=description,
        amount=decimal_amount,
        category=category,
        expense_timing=normalized_expense_timing,
        expense_date=expense_date or cash_session.session_date,
        notes=notes,
    )
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(db: Session, cash_session_id: int) -> list[Expense]:
    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre no existe.")

    return expenses.list_expenses_by_cash_session(
        db=db,
        cash_session_id=cash_session_id,
    )


def _to_money_decimal(amount: Decimal | str | int) -> Decimal:
    if isinstance(amount, float):
        raise ValueError("No usar float para valores monetarios.")
    return Decimal(amount).quantize(MONEY_QUANT)


def _normalize_expense_timing(expense_timing: str) -> str:
    if expense_timing not in VALID_EXPENSE_TIMINGS:
        raise ValueError("El tipo de gasto no es valido.")
    return expense_timing
