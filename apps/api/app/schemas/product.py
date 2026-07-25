from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ProductCategory = Literal[
    "water",
    "bottle",
    "gallon",
    "dispenser",
    "container",
    "other",
]
ProductUnit = Literal[
    "unit",
    "pack",
    "liter",
    "gallon",
    "bottle",
    "container",
    "other",
]
ProductKind = Literal[
    "finished_good",
    "raw_material",
    "supply",
    "packaging",
    "service",
    "other",
]


class ProductCreate(BaseModel):
    sku: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: ProductCategory = "other"
    unit: ProductUnit = "unit"
    presentation: str | None = Field(default=None, max_length=100)
    default_price: Decimal = Field(
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    cost_estimate: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    product_kind: ProductKind = "finished_good"
    production_notes: str | None = None
    is_returnable_container: bool = False
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(value, "El nombre del producto es obligatorio.")

    @field_validator(
        "sku",
        "description",
        "presentation",
        "production_notes",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    category: ProductCategory | None = None
    unit: ProductUnit | None = None
    presentation: str | None = Field(default=None, max_length=100)
    default_price: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    cost_estimate: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    product_kind: ProductKind | None = None
    production_notes: str | None = None
    is_returnable_container: bool | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(value, "El nombre del producto es obligatorio.")

    @field_validator(
        "sku",
        "description",
        "presentation",
        "production_notes",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = {
            "name": self.name,
            "category": self.category,
            "unit": self.unit,
            "default_price": self.default_price,
            "cost_estimate": self.cost_estimate,
            "product_kind": self.product_kind,
            "is_returnable_container": self.is_returnable_container,
        }
        for field_name, value in required_fields.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class ProductRead(BaseModel):
    id: int
    sku: str | None
    name: str
    description: str | None
    category: ProductCategory
    unit: ProductUnit
    presentation: str | None
    default_price: Decimal
    cost_estimate: Decimal
    product_kind: ProductKind
    production_notes: str | None
    is_returnable_container: bool
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductProductionClassificationUpdate(BaseModel):
    product_kind: ProductKind
    production_notes: str | None = None

    @field_validator("production_notes")
    @classmethod
    def normalize_production_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


def _normalize_required_text(value: str, message: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(message)
    return normalized_value


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
