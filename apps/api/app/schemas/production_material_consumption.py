from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.product import ProductKind

ProductionMaterialConsumptionStatus = Literal["active", "voided"]
ProductionMaterialConsumptionState = Literal["not_consumed", "consumed"]


class ProductionMaterialConsumptionSelection(BaseModel):
    production_item_id: int = Field(gt=0)
    recipe_id: int = Field(gt=0)


class ProductionMaterialConsumptionPreviewRequest(BaseModel):
    source_location_id: int = Field(gt=0)
    movement_date: date
    items: list[ProductionMaterialConsumptionSelection] = Field(min_length=1)


class ProductionMaterialConsumptionCreate(
    ProductionMaterialConsumptionPreviewRequest,
):
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ProductionMaterialConsumptionVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class ProductionMaterialConsumptionPreviewItem(BaseModel):
    production_item_id: int
    output_product_name: str
    recipe_id: int
    recipe_name: str
    input_product_id: int
    input_product_name: str
    quantity_consumed: Decimal
    available_stock: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    has_sufficient_stock: bool


class ProductionMaterialConsumptionPreview(BaseModel):
    production_batch_id: int
    source_location_id: int
    total_material_cost: Decimal
    items: list[ProductionMaterialConsumptionPreviewItem]


class ProductionMaterialConsumptionItemRead(BaseModel):
    id: int
    consumption_id: int
    production_item_id: int
    recipe_id: int
    recipe_item_id: int
    input_product_id: int
    input_product_sku_snapshot: str | None
    input_product_name_snapshot: str
    input_product_kind_snapshot: ProductKind
    input_product_presentation_snapshot: str | None
    recipe_number_snapshot: str
    recipe_name_snapshot: str
    quantity_required_base: Decimal
    quantity_consumed: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    inventory_movement_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionMaterialConsumptionRead(BaseModel):
    id: int
    consumption_number: str
    production_batch_id: int
    production_number: str
    source_location_id: int
    source_location_name: str
    movement_date: date
    status: ProductionMaterialConsumptionStatus
    total_material_cost: Decimal
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[ProductionMaterialConsumptionItemRead]

    model_config = ConfigDict(from_attributes=True)


class ProductionBatchMaterialConsumptionRead(BaseModel):
    status: ProductionMaterialConsumptionState
    active_consumption: ProductionMaterialConsumptionRead | None


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
