from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CashCountItemSet(BaseModel):
    cash_session_id: int
    denomination_id: int
    quantity: int = Field(ge=0)


class CashCountItemRead(BaseModel):
    id: int
    cash_session_id: int
    denomination_id: int
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)
