from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

RouteReturnStatus = Literal["active", "voided"]
RouteLoadStatus = Literal["active", "voided"]
InventoryMovementStatus = Literal["active", "voided"]


class RouteReturnItemCreate(BaseModel):
    route_load_item_id: int = Field(gt=0)
    quantity_returned: Decimal = Field(
        gt=Decimal("0.000"),
        max_digits=14,
        decimal_places=3,
    )


class RouteReturnCreate(BaseModel):
    return_date: date
    route_load_id: int = Field(gt=0)
    destination_location_id: int = Field(gt=0)
    notes: str | None = None
    items: list[RouteReturnItemCreate] = Field(min_length=1)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_unique_load_items(self):
        load_item_ids = [item.route_load_item_id for item in self.items]
        if len(load_item_ids) != len(set(load_item_ids)):
            raise ValueError("No se puede repetir un producto en el mismo retorno.")
        return self


class RouteReturnVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class RouteReturnItemRead(BaseModel):
    id: int
    route_return_id: int
    route_load_item_id: int
    product_id: int
    product_sku_snapshot: str | None
    product_name_snapshot: str
    product_presentation_snapshot: str | None
    quantity_loaded: Decimal
    quantity_returned: Decimal
    source_exit_movement_id: int
    destination_entry_movement_id: int
    source_exit_movement_status: InventoryMovementStatus
    destination_entry_movement_status: InventoryMovementStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RouteReturnRead(BaseModel):
    id: int
    return_number: str
    return_date: date
    route_load_id: int
    route_load_number: str
    route_load_status: RouteLoadStatus
    route_id: int
    route_name: str
    vehicle_id: int
    vehicle_name: str
    source_location_id: int
    source_location_name: str
    destination_location_id: int
    destination_location_name: str
    status: RouteReturnStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[RouteReturnItemRead]

    model_config = ConfigDict(from_attributes=True)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
