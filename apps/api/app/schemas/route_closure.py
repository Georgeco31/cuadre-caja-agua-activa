from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RouteClosureStatus = Literal["active", "voided"]
RouteLoadStatus = Literal["active", "voided"]


class RouteClosureCreate(BaseModel):
    closure_date: date
    route_load_id: int = Field(gt=0)
    delivered_cash_total: Decimal = Field(
        ge=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class RouteClosureVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class RouteClosureRead(BaseModel):
    id: int
    closure_number: str
    closure_date: date
    route_load_id: int
    route_load_status: RouteLoadStatus
    route_id: int
    vehicle_id: int
    load_number_snapshot: str
    route_name_snapshot: str
    vehicle_name_snapshot: str
    cash_sales_total: Decimal
    credit_sales_total: Decimal
    payments_total: Decimal
    expected_cash_total: Decimal
    delivered_cash_total: Decimal
    difference_amount: Decimal
    status: RouteClosureStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RouteLoadFinancialClosureRead(BaseModel):
    status: Literal["not_closed", "closed"]
    active_closure: RouteClosureRead | None


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
