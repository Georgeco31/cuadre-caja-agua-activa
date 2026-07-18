from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VehicleType = Literal["truck", "van", "motorcycle", "car", "other"]
FuelType = Literal["gasoline", "diesel", "electric", "hybrid", "other"]


class VehicleCreate(BaseModel):
    code: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    plate: str | None = Field(default=None, max_length=50)
    vehicle_type: VehicleType = "other"
    brand: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    year: int | None = Field(default=None, ge=1900, le=2100)
    color: str | None = Field(default=None, max_length=80)
    fuel_type: FuelType = "other"
    capacity_reference: str | None = Field(default=None, max_length=255)
    reference_driver: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(value, "El nombre del vehiculo es obligatorio.")

    @field_validator(
        "code",
        "plate",
        "brand",
        "model",
        "color",
        "capacity_reference",
        "reference_driver",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class VehicleUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, max_length=255)
    plate: str | None = Field(default=None, max_length=50)
    vehicle_type: VehicleType | None = None
    brand: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    year: int | None = Field(default=None, ge=1900, le=2100)
    color: str | None = Field(default=None, max_length=80)
    fuel_type: FuelType | None = None
    capacity_reference: str | None = Field(default=None, max_length=255)
    reference_driver: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(value, "El nombre del vehiculo es obligatorio.")

    @field_validator(
        "code",
        "plate",
        "brand",
        "model",
        "color",
        "capacity_reference",
        "reference_driver",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = {
            "name": self.name,
            "vehicle_type": self.vehicle_type,
            "fuel_type": self.fuel_type,
        }
        for field_name, value in required_fields.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class VehicleRead(BaseModel):
    id: int
    code: str | None
    name: str
    plate: str | None
    vehicle_type: VehicleType
    brand: str | None
    model: str | None
    year: int | None
    color: str | None
    fuel_type: FuelType
    capacity_reference: str | None
    reference_driver: str | None
    is_active: bool
    notes: str | None
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
