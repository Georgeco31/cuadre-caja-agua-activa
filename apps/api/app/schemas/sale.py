from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SalePaymentMethod = Literal["cash", "transfer", "card", "other"]
SaleStatus = Literal["active", "voided"]
SaleType = Literal["cash", "credit"]
CreditStatus = Literal["none", "pending", "paid", "voided"]


class SaleItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=Decimal("0"),
        max_digits=12,
        decimal_places=3,
    )
    unit_price: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )


class CashSaleCreate(BaseModel):
    sale_date: date
    customer_id: int | None = Field(default=None, gt=0)
    route_load_id: int | None = Field(default=None, gt=0)
    payment_method: SalePaymentMethod = "cash"
    notes: str | None = None
    items: list[SaleItemCreate] = Field(min_length=1)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class CreditSaleCreate(BaseModel):
    sale_date: date
    customer_id: int = Field(gt=0)
    route_load_id: int | None = Field(default=None, gt=0)
    due_date: date | None = None
    notes: str | None = None
    items: list[SaleItemCreate] = Field(min_length=1)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class SaleVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class SaleDateCorrectionCreate(BaseModel):
    new_sale_date: date
    reason: str = Field(min_length=1, max_length=1000)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de corrección es obligatorio.")
        return normalized_value


class SaleItemRead(BaseModel):
    id: int
    sale_id: int
    product_id: int
    product_sku_snapshot: str | None
    product_name_snapshot: str
    product_presentation_snapshot: str | None
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    price_source: str | None
    price_list_id: int | None
    price_list_name_snapshot: str | None
    pricing_note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SaleRead(BaseModel):
    id: int
    sale_number: str
    sale_date: date
    customer_id: int | None
    customer_name_snapshot: str
    route_load_id: int | None
    route_load_number: str | None
    route_name: str | None
    route_vehicle_name: str | None
    route_load_status: SaleStatus | None
    sale_type: SaleType
    payment_method: SalePaymentMethod
    status: SaleStatus
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    credit_status: CreditStatus
    due_date: date | None
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[SaleItemRead]

    model_config = ConfigDict(from_attributes=True)


class SaleDateCorrectionResponse(BaseModel):
    sale: SaleRead
    correction_id: int
    correction_type: Literal["date_change"]
    previous_sale_date: date
    new_sale_date: date
    reason: str
    corrected_by: int
    corrected_at: datetime


class CustomerCreditBalance(BaseModel):
    customer_id: int
    customer_name: str
    total_credit_sales: Decimal
    total_paid: Decimal
    total_balance: Decimal


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
