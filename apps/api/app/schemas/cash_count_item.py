from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CashCountItemSet(BaseModel):
    denomination_id: int
    quantity: int


class CashCountItemRead(BaseModel):
    id: int
    cash_session_id: int
    denomination_id: int
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)
