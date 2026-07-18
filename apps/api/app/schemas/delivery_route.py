from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DeliveryRouteCreate(BaseModel):
    code: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    zone: str | None = Field(default=None, max_length=120)
    sector: str | None = Field(default=None, max_length=120)
    service_days: str | None = Field(default=None, max_length=255)
    reference_driver: str | None = Field(default=None, max_length=255)
    reference_vehicle: str | None = Field(default=None, max_length=255)
    expected_daily_cash: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(value, "El nombre de la ruta es obligatorio.")

    @field_validator(
        "code",
        "description",
        "zone",
        "sector",
        "service_days",
        "reference_driver",
        "reference_vehicle",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class DeliveryRouteUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    zone: str | None = Field(default=None, max_length=120)
    sector: str | None = Field(default=None, max_length=120)
    service_days: str | None = Field(default=None, max_length=255)
    reference_driver: str | None = Field(default=None, max_length=255)
    reference_vehicle: str | None = Field(default=None, max_length=255)
    expected_daily_cash: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(value, "El nombre de la ruta es obligatorio.")

    @field_validator(
        "code",
        "description",
        "zone",
        "sector",
        "service_days",
        "reference_driver",
        "reference_vehicle",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = {
            "name": self.name,
            "expected_daily_cash": self.expected_daily_cash,
        }
        for field_name, value in required_fields.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class DeliveryRouteRead(BaseModel):
    id: int
    code: str | None
    name: str
    description: str | None
    zone: str | None
    sector: str | None
    service_days: str | None
    reference_driver: str | None
    reference_vehicle: str | None
    expected_daily_cash: Decimal
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
