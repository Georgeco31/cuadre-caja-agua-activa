from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ProductionStatus = Literal["active", "voided"]


class ProductionItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_produced: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=3,
    )
    quantity_waste: Decimal = Field(
        default=Decimal("0.000"),
        ge=Decimal("0"),
        max_digits=14,
        decimal_places=3,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_waste_not_greater_than_produced(self):
        if self.quantity_waste > self.quantity_produced:
            raise ValueError(
                "La merma no puede ser mayor que la cantidad producida.",
            )
        return self


class ProductionBatchCreate(BaseModel):
    production_date: date
    notes: str | None = None
    items: list[ProductionItemCreate] = Field(min_length=1)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ProductionBatchVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class ProductionItemRead(BaseModel):
    id: int
    production_batch_id: int
    product_id: int
    product_sku_snapshot: str | None
    product_name_snapshot: str
    product_presentation_snapshot: str | None
    quantity_produced: Decimal
    quantity_waste: Decimal
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionBatchRead(BaseModel):
    id: int
    production_number: str
    production_date: date
    status: ProductionStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[ProductionItemRead]

    model_config = ConfigDict(from_attributes=True)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
