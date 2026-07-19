from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProductionInventoryApplicationStatus = Literal["active", "voided"]
ProductionInventoryState = Literal["not_applied", "applied", "voided"]


class ProductionInventoryApply(BaseModel):
    location_id: int = Field(gt=0)
    movement_date: date
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ProductionInventoryApplicationVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class ProductionInventoryApplicationItemRead(BaseModel):
    id: int
    application_id: int
    production_item_id: int
    product_id: int
    inventory_movement_id: int
    movement_date: date
    quantity_applied: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionInventoryApplicationRead(BaseModel):
    state: ProductionInventoryState
    application_id: int | None
    production_batch_id: int
    location_id: int | None
    location_name: str | None
    status: ProductionInventoryApplicationStatus | None
    applied_at: datetime | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int | None
    created_at: datetime | None
    updated_at: datetime | None
    items: list[ProductionInventoryApplicationItemRead]


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
