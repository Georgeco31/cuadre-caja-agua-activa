from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

ExpenseTiming = Literal["before_count", "after_count"]


class ExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    category: str | None = None
    expense_timing: ExpenseTiming = "after_count"
    expense_date: date | None = None
    notes: str | None = None


class ExpenseRead(BaseModel):
    id: int
    cash_session_id: int
    description: str
    amount: Decimal
    category: str | None
    expense_timing: ExpenseTiming
    expense_date: date
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
