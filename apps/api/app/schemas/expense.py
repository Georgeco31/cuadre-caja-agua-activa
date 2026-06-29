from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    cash_session_id: int
    description: str
    amount: Decimal = Field(gt=0)
    category: str | None = None
    expense_date: date | None = None
    notes: str | None = None


class ExpenseRead(BaseModel):
    id: int
    cash_session_id: int
    description: str
    amount: Decimal
    category: str | None
    expense_date: date
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
