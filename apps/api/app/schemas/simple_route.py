from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SimpleRouteStatus = Literal["draft", "in_progress", "settled", "cancelled"]
SimpleRouteSaleType = Literal["cash", "credit", "partial"]
SimpleRouteMovementType = Literal["out", "return"]
SimpleRouteItemCategory = Literal[
    "full_jug",
    "empty_jug",
    "gallon",
    "pack",
    "loaned_jug",
    "returned_jug",
    "jug_to_refill",
    "refilled_jug",
    "other",
]
SimpleRouteExpenseCategory = Literal[
    "fuel",
    "lunch",
    "glue",
    "cap_removal",
    "other",
]


class SimpleRouteSheetCreate(BaseModel):
    route_date: date
    seller_name: str = Field(min_length=1, max_length=255)
    employee_id: int | None = Field(default=None, gt=0)
    vehicle_id: int | None = Field(default=None, gt=0)
    route_label: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("seller_name")
    @classmethod
    def normalize_seller_name(cls, value: str) -> str:
        return _required_text(value, "El vendedor es obligatorio.")

    @field_validator("route_label", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteSheetUpdate(BaseModel):
    route_date: date | None = None
    seller_name: str | None = Field(default=None, max_length=255)
    employee_id: int | None = Field(default=None, gt=0)
    vehicle_id: int | None = Field(default=None, gt=0)
    route_label: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("seller_name")
    @classmethod
    def normalize_optional_seller(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _required_text(value, "El vendedor no puede quedar vacío.")

    @field_validator("route_label", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteTripCreate(BaseModel):
    trip_number: int | None = Field(default=None, gt=0)
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteTripUpdate(BaseModel):
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteTripItemCreate(BaseModel):
    movement_type: SimpleRouteMovementType
    product_id: int | None = Field(default=None, gt=0)
    item_label: str | None = Field(default=None, max_length=255)
    item_category: SimpleRouteItemCategory = "other"
    quantity: Decimal = Field(gt=Decimal("0"), max_digits=14, decimal_places=3)
    notes: str | None = None

    @field_validator("item_label", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteSaleItemCreate(BaseModel):
    product_id: int | None = Field(default=None, gt=0)
    product_name: str | None = Field(default=None, max_length=255)
    item_category: SimpleRouteItemCategory = "other"
    quantity: Decimal = Field(gt=Decimal("0"), max_digits=14, decimal_places=3)
    unit_price: Decimal = Field(
        ge=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )

    @field_validator("product_name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteSaleCreate(BaseModel):
    customer_id: int | None = Field(default=None, gt=0)
    customer_name: str | None = Field(default=None, max_length=255)
    sale_type: SimpleRouteSaleType
    sale_date: date | None = None
    paid_amount: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )
    notes: str | None = None
    items: list[SimpleRouteSaleItemCreate] = Field(min_length=1)

    @field_validator("customer_name", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteCollectionCreate(BaseModel):
    simple_route_sale_id: int | None = Field(default=None, gt=0)
    customer_id: int | None = Field(default=None, gt=0)
    customer_name: str | None = Field(default=None, max_length=255)
    amount: Decimal = Field(gt=Decimal("0"), max_digits=14, decimal_places=2)
    collection_date: date | None = None
    notes: str | None = None

    @field_validator("customer_name", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    category: SimpleRouteExpenseCategory = "other"
    amount: Decimal = Field(gt=Decimal("0"), max_digits=14, decimal_places=2)
    expense_date: date | None = None
    notes: str | None = None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return _required_text(value, "La descripción del gasto es obligatoria.")

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteSettle(BaseModel):
    cash_delivered: Decimal = Field(
        ge=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteCancel(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        return _required_text(value, "El motivo de cancelación es obligatorio.")


class SimpleRouteCashReceiptCreate(BaseModel):
    cash_session_id: int = Field(gt=0)
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _optional_text(value)


class SimpleRouteTripItemRead(BaseModel):
    id: int
    movement_type: SimpleRouteMovementType
    product_id: int | None
    item_label: str
    item_category: SimpleRouteItemCategory
    quantity: Decimal
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteTripRead(BaseModel):
    id: int
    route_sheet_id: int
    trip_number: int
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[SimpleRouteTripItemRead]

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteSaleItemRead(BaseModel):
    id: int
    product_id: int | None
    product_name_snapshot: str
    item_category: SimpleRouteItemCategory
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteSaleRead(BaseModel):
    id: int
    route_sheet_id: int
    customer_id: int | None
    customer_name_snapshot: str | None
    sale_type: SimpleRouteSaleType
    sale_date: date
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    remaining_amount: Decimal
    status: Literal["active", "voided"]
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[SimpleRouteSaleItemRead]

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteCollectionRead(BaseModel):
    id: int
    route_sheet_id: int
    simple_route_sale_id: int | None
    customer_id: int | None
    customer_name_snapshot: str | None
    amount: Decimal
    collection_date: date
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteExpenseRead(BaseModel):
    id: int
    route_sheet_id: int
    description: str
    amount: Decimal
    category: SimpleRouteExpenseCategory
    expense_date: date
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteAuditLogRead(BaseModel):
    id: int
    route_sheet_id: int
    action: str
    reason: str | None
    created_by: int
    created_at: datetime
    metadata_json: str | None

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteCashReceiptRead(BaseModel):
    id: int
    route_sheet_id: int
    cash_session_id: int
    amount: Decimal
    received_by: int
    received_at: datetime
    notes: str | None
    created_at: datetime
    seller_name: str | None = None
    route_label: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteSheetRead(BaseModel):
    id: int
    route_date: date
    seller_name: str
    employee_id: int | None
    employee_name: str | None
    vehicle_id: int | None
    vehicle_name: str | None
    route_label: str | None
    status: SimpleRouteStatus
    cash_delivered: Decimal | None
    cash_received_in_cash_session: bool
    cash_session_id: int | None
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    settled_by: int | None
    settled_at: datetime | None
    cancelled_by: int | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    trips: list[SimpleRouteTripRead]
    sales: list[SimpleRouteSaleRead]
    collections: list[SimpleRouteCollectionRead]
    expenses: list[SimpleRouteExpenseRead]
    audit_logs: list[SimpleRouteAuditLogRead]
    cash_receipt: SimpleRouteCashReceiptRead | None

    model_config = ConfigDict(from_attributes=True)


class SimpleRouteProductSettlement(BaseModel):
    product_id: int | None
    item_label: str
    item_category: SimpleRouteItemCategory
    total_out: Decimal
    total_returned: Decimal
    physical_sold: Decimal
    registered_sold: Decimal
    physical_difference: Decimal


class SimpleRouteSettlementRead(BaseModel):
    route_sheet_id: int
    status: Literal["pending", "balanced", "with_difference", "cancelled"]
    products: list[SimpleRouteProductSettlement]
    route_sales_total: Decimal
    cash_sales_collected: Decimal
    partial_sales_collected: Decimal
    route_credit_total: Decimal
    collections_total: Decimal
    expenses_total: Decimal
    expected_cash: Decimal
    cash_delivered: Decimal | None
    cash_difference: Decimal | None
    cash_receipt_status: Literal["pending", "received"]
    cash_session_id: int | None


class SimpleRouteListItem(BaseModel):
    id: int
    route_date: date
    seller_name: str
    vehicle_name: str | None
    route_label: str | None
    status: SimpleRouteStatus
    route_sales_total: Decimal
    route_credit_total: Decimal
    expenses_total: Decimal
    expected_cash: Decimal
    cash_delivered: Decimal | None
    cash_difference: Decimal | None
    settlement_status: str
    cash_received_in_cash_session: bool


class SimpleRouteAnalyticsRanking(BaseModel):
    label: str
    total: Decimal
    count: int


class SimpleRouteAnalyticsTrend(BaseModel):
    route_date: date
    total: Decimal


class SimpleRouteAnalyticsRead(BaseModel):
    date_from: date
    date_to: date
    routes_count: int
    total_route_sales: Decimal
    total_cash_sales: Decimal
    total_credit_sales: Decimal
    total_collected: Decimal
    total_expenses: Decimal
    total_expected_cash: Decimal
    total_delivered_cash: Decimal
    total_difference: Decimal
    top_routes: list[SimpleRouteAnalyticsRanking]
    top_sellers: list[SimpleRouteAnalyticsRanking]
    best_sales_day: SimpleRouteAnalyticsTrend | None
    daily_trend: list[SimpleRouteAnalyticsTrend]
    routes_with_differences: list[int]


class SimpleRouteAugustDryRunCandidate(BaseModel):
    sale_id: int
    sale_number: str
    customer: str
    sale_type: str
    status: str
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    payments_total: Decimal
    route_load_id: int
    route_closure_id: int | None
    cash_session_id: int | None
    cash_session_status: str | None
    could_be_voided: bool
    risk: str
    suggested_reason: str


class SimpleRouteAugustDryRunRead(BaseModel):
    report_date: date
    candidates_count: int
    candidates: list[SimpleRouteAugustDryRunCandidate]
    modified_records: int = 0
    warning: str


def _required_text(value: str, message: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(message)
    return normalized


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
