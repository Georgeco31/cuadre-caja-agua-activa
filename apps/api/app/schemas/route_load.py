from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

RouteLoadStatus = Literal["active", "voided"]
InventoryMovementStatus = Literal["active", "voided"]


class RouteLoadItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_loaded: Decimal = Field(
        gt=Decimal("0.000"),
        max_digits=14,
        decimal_places=3,
    )


class RouteLoadCreate(BaseModel):
    load_date: date
    route_id: int = Field(gt=0)
    vehicle_id: int = Field(gt=0)
    source_location_id: int = Field(gt=0)
    destination_location_id: int = Field(gt=0)
    notes: str | None = None
    items: list[RouteLoadItemCreate] = Field(min_length=1)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_locations_and_products(self):
        if self.source_location_id == self.destination_location_id:
            raise ValueError("Las ubicaciones de origen y destino deben ser distintas.")
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("No se puede repetir un producto en la misma carga.")
        return self


class RouteLoadVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class RouteLoadItemRead(BaseModel):
    id: int
    route_load_id: int
    product_id: int
    product_sku_snapshot: str | None
    product_name_snapshot: str
    product_presentation_snapshot: str | None
    quantity_loaded: Decimal
    source_exit_movement_id: int
    destination_entry_movement_id: int
    source_exit_movement_status: InventoryMovementStatus
    destination_entry_movement_status: InventoryMovementStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RouteLoadRead(BaseModel):
    id: int
    load_number: str
    load_date: date
    route_id: int
    route_name: str
    vehicle_id: int
    vehicle_name: str
    source_location_id: int
    source_location_name: str
    destination_location_id: int
    destination_location_name: str
    status: RouteLoadStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[RouteLoadItemRead]

    model_config = ConfigDict(from_attributes=True)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
