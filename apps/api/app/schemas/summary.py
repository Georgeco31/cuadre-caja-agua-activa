from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CashSessionSummary(BaseModel):
    cash_session_id: int
    session_date: date
    status: str
    total_coins: Decimal
    total_bills: Decimal
    total_counted: Decimal
    total_pre_count_expenses: Decimal
    total_post_count_expenses: Decimal
    total_expenses: Decimal
    final_total: Decimal
