from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

InventoryLocationType = Literal[
    "warehouse",
    "vehicle",
    "production_area",
    "other",
]
InventoryMovementType = Literal[
    "entry",
    "exit",
    "adjustment_in",
    "adjustment_out",
]
InventoryMovementStatus = Literal["active", "voided"]


class InventoryLocationCreate(BaseModel):
    code: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    location_type: InventoryLocationType = "warehouse"
    vehicle_id: int | None = Field(default=None, gt=0)
    description: str | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El nombre de la ubicacion es obligatorio.",
        )

    @field_validator("code", "description", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class InventoryLocationUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, max_length=255)
    location_type: InventoryLocationType | None = None
    vehicle_id: int | None = Field(default=None, gt=0)
    description: str | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(
            value,
            "El nombre de la ubicacion es obligatorio.",
        )

    @field_validator("code", "description", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for field_name, value in {
            "name": self.name,
            "location_type": self.location_type,
        }.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class InventoryLocationRead(BaseModel):
    id: int
    code: str | None
    name: str
    location_type: InventoryLocationType
    vehicle_id: int | None
    description: str | None
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryStockRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str | None
    product_presentation: str | None
    location_id: int
    location_name: str
    quantity_on_hand: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryMovementCreate(BaseModel):
    movement_date: date
    movement_type: InventoryMovementType
    product_id: int = Field(gt=0)
    location_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=Decimal("0.000"),
        max_digits=14,
        decimal_places=3,
    )
    unit_cost: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    reason: str | None = None

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class InventoryMovementVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo de anulacion es obligatorio.",
        )


class InventoryMovementRead(BaseModel):
    id: int
    movement_date: date
    movement_type: InventoryMovementType
    product_id: int
    location_id: int
    location_name: str
    product_sku_snapshot: str | None
    product_name_snapshot: str
    product_presentation_snapshot: str | None
    quantity: Decimal
    unit_cost: Decimal | None
    total_cost: Decimal | None
    reason: str | None
    status: InventoryMovementStatus
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

