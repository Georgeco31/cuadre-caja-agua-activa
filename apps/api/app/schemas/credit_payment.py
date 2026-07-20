from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CreditPaymentMethod = Literal["cash", "transfer", "card", "other"]
CreditPaymentStatus = Literal["active", "voided"]
CreditSaleStatus = Literal["pending", "paid", "voided"]


class CreditPaymentCreate(BaseModel):
    payment_date: date
    route_load_id: int | None = Field(default=None, gt=0)
    amount: Decimal = Field(
        gt=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    payment_method: CreditPaymentMethod
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class CreditPaymentVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class CreditPaymentRead(BaseModel):
    id: int
    sale_id: int
    sale_number: str
    customer_id: int
    customer_name: str
    route_load_id: int | None
    route_load_number: str | None
    route_name: str | None
    route_vehicle_name: str | None
    route_load_status: CreditPaymentStatus | None
    payment_date: date
    amount: Decimal
    payment_method: CreditPaymentMethod
    status: CreditPaymentStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    sale_paid_amount: Decimal
    sale_balance_amount: Decimal
    sale_credit_status: CreditSaleStatus

    model_config = ConfigDict(from_attributes=True)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
