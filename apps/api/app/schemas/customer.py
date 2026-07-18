from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CustomerType = Literal[
    "household",
    "store",
    "business",
    "distributor",
    "other",
]


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    primary_phone: str | None = Field(default=None, max_length=50)
    secondary_phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    sector: str | None = Field(default=None, max_length=120)
    customer_type: CustomerType = "household"
    route_reference: str | None = Field(default=None, max_length=150)
    credit_allowed: bool = False
    credit_limit: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(value, "El nombre del cliente es obligatorio.")

    @field_validator(
        "primary_phone",
        "secondary_phone",
        "address",
        "sector",
        "route_reference",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    primary_phone: str | None = Field(default=None, max_length=50)
    secondary_phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    sector: str | None = Field(default=None, max_length=120)
    customer_type: CustomerType | None = None
    route_reference: str | None = Field(default=None, max_length=150)
    credit_allowed: bool | None = None
    credit_limit: Decimal | None = Field(
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
        return _normalize_required_text(value, "El nombre del cliente es obligatorio.")

    @field_validator(
        "primary_phone",
        "secondary_phone",
        "address",
        "sector",
        "route_reference",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = {
            "name": self.name,
            "customer_type": self.customer_type,
            "credit_allowed": self.credit_allowed,
            "credit_limit": self.credit_limit,
        }
        for field_name, value in required_fields.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class CustomerRead(BaseModel):
    id: int
    name: str
    primary_phone: str | None
    secondary_phone: str | None
    address: str | None
    sector: str | None
    customer_type: CustomerType
    route_reference: str | None
    credit_allowed: bool
    credit_limit: Decimal
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
