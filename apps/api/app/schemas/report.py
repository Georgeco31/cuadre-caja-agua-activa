from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CashSummaryReport(BaseModel):
    date_from: date | None
    date_to: date | None
    status: str | None
    total_sessions: int
    open_sessions: int
    closed_sessions: int
    total_counted: Decimal
    total_pre_count_expenses: Decimal
    total_post_count_expenses: Decimal
    total_expenses: Decimal
    final_total: Decimal
