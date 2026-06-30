from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.cash_count_item import CashCountItemRead
from app.schemas.expense import ExpenseRead
from app.schemas.summary import CashSessionSummary


class CorrectionCountItemCreate(BaseModel):
    denomination_id: int
    quantity: int
    reason: str


class CorrectionExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    category: str | None = None
    expense_date: date | None = None
    notes: str | None = None
    reason: str


class CorrectionLogRead(BaseModel):
    id: int
    cash_session_id: int
    reason: str
    previous_total: Decimal
    new_total: Decimal
    created_by: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CorrectionCountItemResponse(BaseModel):
    count_item: CashCountItemRead
    summary: CashSessionSummary
    correction_log: CorrectionLogRead


class CorrectionExpenseResponse(BaseModel):
    expense: ExpenseRead
    summary: CashSessionSummary
    correction_log: CorrectionLogRead
