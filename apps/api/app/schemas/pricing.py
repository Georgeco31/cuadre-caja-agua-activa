from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PriceListType = Literal[
    "general",
    "customer",
    "route",
    "customer_route",
    "special",
]
PriceSource = Literal[
    "default",
    "general",
    "special",
    "customer",
    "route",
    "customer_route",
    "manual",
]


class PriceListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    list_type: PriceListType
    customer_id: int | None = Field(default=None, gt=0)
    route_id: int | None = Field(default=None, gt=0)
    priority: int = 0
    valid_from: date | None = None
    valid_to: date | None = None
    is_active: bool = True
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El nombre de la lista es obligatorio.")
        return normalized_value

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_target_and_dates(self):
        _validate_target(self.list_type, self.customer_id, self.route_id)
        _validate_dates(self.valid_from, self.valid_to)
        return self


class PriceListUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    list_type: PriceListType | None = None
    customer_id: int | None = Field(default=None, gt=0)
    route_id: int | None = Field(default=None, gt=0)
    priority: int | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El nombre de la lista es obligatorio.")
        return normalized_value

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class PriceListItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    unit_price: Decimal = Field(
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    min_quantity: Decimal = Field(
        default=Decimal("1.000"),
        gt=Decimal("0"),
        max_digits=12,
        decimal_places=3,
    )
    is_active: bool = True
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class PriceListItemUpdate(BaseModel):
    product_id: int | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    min_quantity: Decimal | None = Field(
        default=None,
        gt=Decimal("0"),
        max_digits=12,
        decimal_places=3,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class PriceListItemRead(BaseModel):
    id: int
    price_list_id: int
    product_id: int
    product_name: str
    product_sku: str | None
    product_presentation: str | None
    unit_price: Decimal
    min_quantity: Decimal
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceListRead(BaseModel):
    id: int
    name: str
    list_type: PriceListType
    customer_id: int | None
    customer_name: str | None
    route_id: int | None
    route_name: str | None
    priority: int
    valid_from: date | None
    valid_to: date | None
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[PriceListItemRead]

    model_config = ConfigDict(from_attributes=True)


class PriceResolution(BaseModel):
    product_id: int
    default_price: Decimal
    resolved_price: Decimal
    price_source: PriceSource
    price_list_id: int | None
    price_list_name: str | None
    pricing_note: str


def _validate_target(
    list_type: PriceListType,
    customer_id: int | None,
    route_id: int | None,
) -> None:
    if list_type == "customer" and customer_id is None:
        raise ValueError("Una lista por cliente requiere customer_id.")
    if list_type == "route" and route_id is None:
        raise ValueError("Una lista por ruta requiere route_id.")
    if list_type == "customer_route" and (
        customer_id is None or route_id is None
    ):
        raise ValueError(
            "Una lista por cliente y ruta requiere customer_id y route_id."
        )


def _validate_dates(valid_from: date | None, valid_to: date | None) -> None:
    if valid_from is not None and valid_to is not None and valid_from > valid_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
