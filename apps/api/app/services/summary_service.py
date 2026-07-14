from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cash_count_item import CashCountItem
from app.models.denomination import Denomination
from app.models.expense import Expense
from app.repositories import cash_sessions
from app.schemas.summary import CashSessionSummary
from app.services.expense_service import (
    EXPENSE_TIMING_AFTER_COUNT,
    EXPENSE_TIMING_BEFORE_COUNT,
)

MONEY_ZERO = Decimal("0.00")


def get_cash_session_summary(
    db: Session,
    cash_session_id: int,
) -> CashSessionSummary:
    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre no existe.")

    total_coins = _sum_count_items_by_type(db, cash_session_id, "coin")
    total_bills = _sum_count_items_by_type(db, cash_session_id, "bill")
    total_counted = total_coins + total_bills
    total_pre_count_expenses = _sum_expenses(
        db,
        cash_session_id,
        EXPENSE_TIMING_BEFORE_COUNT,
    )
    total_post_count_expenses = _sum_expenses(
        db,
        cash_session_id,
        EXPENSE_TIMING_AFTER_COUNT,
    )
    final_total = total_counted - total_post_count_expenses

    return CashSessionSummary(
        cash_session_id=cash_session.id,
        session_date=cash_session.session_date,
        status=cash_session.status,
        total_coins=total_coins,
        total_bills=total_bills,
        total_counted=total_counted,
        total_pre_count_expenses=total_pre_count_expenses,
        total_post_count_expenses=total_post_count_expenses,
        total_expenses=total_post_count_expenses,
        final_total=final_total,
    )


def _sum_count_items_by_type(
    db: Session,
    cash_session_id: int,
    denomination_type: str,
) -> Decimal:
    statement = (
        select(CashCountItem.subtotal)
        .join(Denomination)
        .where(
            CashCountItem.cash_session_id == cash_session_id,
            Denomination.type == denomination_type,
        )
    )
    return sum(db.scalars(statement), MONEY_ZERO)


def _sum_expenses(
    db: Session,
    cash_session_id: int,
    expense_timing: str,
) -> Decimal:
    statement = select(Expense.amount).where(
        Expense.cash_session_id == cash_session_id,
        Expense.expense_timing == expense_timing,
    )
    return sum(db.scalars(statement), MONEY_ZERO)
