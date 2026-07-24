from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RouteCashReceiptStatus = Literal["active", "voided"]


class RouteCashReceiptCreate(BaseModel):
    receipt_date: date
    route_closure_id: int = Field(gt=0)
    cash_session_id: int = Field(gt=0)
    received_amount: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class RouteCashReceiptVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class RouteClosureReceiptContext(BaseModel):
    id: int
    closure_number: str
    closure_date: date
    route_load_id: int
    route_id: int
    vehicle_id: int
    delivered_cash_total: Decimal
    status: Literal["active", "voided"]

    model_config = ConfigDict(from_attributes=True)


class CashSessionReceiptContext(BaseModel):
    id: int
    session_date: date
    status: Literal["open", "closed", "corrected"]

    model_config = ConfigDict(from_attributes=True)


class RouteCashReceiptRead(BaseModel):
    id: int
    receipt_number: str
    receipt_date: date
    route_closure_id: int
    cash_session_id: int
    route_load_id: int
    route_id: int
    vehicle_id: int
    closure_number_snapshot: str
    route_name_snapshot: str
    vehicle_name_snapshot: str
    delivered_cash_total: Decimal
    received_amount: Decimal
    difference_amount: Decimal
    status: RouteCashReceiptStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    route_closure: RouteClosureReceiptContext
    cash_session: CashSessionReceiptContext

    model_config = ConfigDict(from_attributes=True)


class RouteClosureCashReceiptRead(BaseModel):
    status: Literal["not_received", "received"]
    active_receipt: RouteCashReceiptRead | None


class RouteCashReceiptTotals(BaseModel):
    receipts_count: int
    delivered_cash_total: Decimal
    received_amount_total: Decimal
    difference_total: Decimal


class CashSessionRouteCashReceiptsRead(BaseModel):
    cash_session_id: int
    session_date: date
    status: Literal["open", "closed", "corrected"]
    receipts: list[RouteCashReceiptRead]
    totals: RouteCashReceiptTotals


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
