from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    identification: str | None = Field(default=None, max_length=80)
    primary_phone: str | None = Field(default=None, max_length=50)
    secondary_phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    supplier_type: str | None = Field(default=None, max_length=80)
    payment_terms: str | None = Field(default=None, max_length=120)
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El nombre del proveedor es obligatorio.",
        )

    @field_validator(
        "identification",
        "primary_phone",
        "secondary_phone",
        "email",
        "address",
        "contact_name",
        "supplier_type",
        "payment_terms",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    identification: str | None = Field(default=None, max_length=80)
    primary_phone: str | None = Field(default=None, max_length=50)
    secondary_phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    supplier_type: str | None = Field(default=None, max_length=80)
    payment_terms: str | None = Field(default=None, max_length=120)
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(
            value,
            "El nombre del proveedor es obligatorio.",
        )

    @field_validator(
        "identification",
        "primary_phone",
        "secondary_phone",
        "email",
        "address",
        "contact_name",
        "supplier_type",
        "payment_terms",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_name(self):
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("El nombre del proveedor no puede ser nulo.")
        return self


class SupplierRead(BaseModel):
    id: int
    name: str
    identification: str | None
    primary_phone: str | None
    secondary_phone: str | None
    email: str | None
    address: str | None
    contact_name: str | None
    supplier_type: str | None
    payment_terms: str | None
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
