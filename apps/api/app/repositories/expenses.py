from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.expense import Expense


def create_expense(
    db: Session,
    cash_session_id: int,
    description: str,
    amount: Decimal,
    category: str | None,
    expense_date: date,
    notes: str | None,
) -> Expense:
    expense = Expense(
        cash_session_id=cash_session_id,
        description=description,
        amount=amount,
        category=category,
        expense_date=expense_date,
        notes=notes,
    )
    db.add(expense)
    return expense


def list_expenses_by_cash_session(
    db: Session,
    cash_session_id: int,
) -> list[Expense]:
    statement = select(Expense).where(Expense.cash_session_id == cash_session_id)
    return list(db.scalars(statement))
