from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.product import ProductKind

ProductionRecipeStatus = Literal["active", "inactive", "voided"]


class ProductionRecipeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    output_product_id: int = Field(gt=0)
    output_quantity: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=3,
    )
    valid_from: date | None = None
    valid_to: date | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El nombre de la formula es obligatorio.",
        )

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_dates(self):
        _validate_dates(self.valid_from, self.valid_to)
        return self


class ProductionRecipeUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    output_product_id: int | None = Field(default=None, gt=0)
    output_quantity: Decimal | None = Field(
        default=None,
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=3,
    )
    valid_from: date | None = None
    valid_to: date | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(
            value,
            "El nombre de la formula es obligatorio.",
        )

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for field_name in ("name", "output_product_id", "output_quantity"):
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class ProductionRecipeVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo de anulacion es obligatorio.",
        )


class ProductionRecipeItemCreate(BaseModel):
    input_product_id: int = Field(gt=0)
    quantity_required: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=3,
    )
    unit_cost: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=16,
        decimal_places=4,
    )
    waste_percentage: Decimal = Field(
        default=Decimal("0"),
        ge=Decimal("0"),
        max_digits=7,
        decimal_places=3,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ProductionRecipeItemUpdate(BaseModel):
    input_product_id: int | None = Field(default=None, gt=0)
    quantity_required: Decimal | None = Field(
        default=None,
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=3,
    )
    unit_cost: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=16,
        decimal_places=4,
    )
    waste_percentage: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        max_digits=7,
        decimal_places=3,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for field_name in (
            "input_product_id",
            "quantity_required",
            "unit_cost",
            "waste_percentage",
        ):
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class ProductionRecipeItemRead(BaseModel):
    id: int
    recipe_id: int
    input_product_id: int
    input_product_sku_snapshot: str | None
    input_product_name_snapshot: str
    input_product_kind_snapshot: ProductKind
    input_product_presentation_snapshot: str | None
    quantity_required: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    waste_percentage: Decimal
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionRecipeRead(BaseModel):
    id: int
    recipe_number: str
    name: str
    output_product_id: int
    output_product_name: str
    output_product_kind: ProductKind
    output_quantity: Decimal
    status: ProductionRecipeStatus
    valid_from: date | None
    valid_to: date | None
    estimated_material_cost: Decimal
    estimated_cost_per_unit: Decimal
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[ProductionRecipeItemRead]

    model_config = ConfigDict(from_attributes=True)


class ProductionRecipeCostItem(BaseModel):
    input_product_id: int
    input_product_name_snapshot: str
    quantity_required_base: Decimal
    quantity_required_scaled: Decimal
    unit_cost: Decimal
    total_cost_scaled: Decimal


class ProductionRecipeCostEstimate(BaseModel):
    recipe_id: int
    recipe_number: str
    output_product_id: int
    output_product_name: str
    base_output_quantity: Decimal
    requested_output_quantity: Decimal
    estimated_material_cost: Decimal
    estimated_cost_per_unit: Decimal
    items: list[ProductionRecipeCostItem]


def _validate_dates(valid_from: date | None, valid_to: date | None) -> None:
    if valid_from is not None and valid_to is not None and valid_from > valid_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


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
