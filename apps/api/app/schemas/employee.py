from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

EmployeeType = Literal[
    "driver",
    "assistant",
    "office",
    "production",
    "sales",
    "other",
]
PaymentFrequency = Literal[
    "daily",
    "weekly",
    "biweekly",
    "monthly",
    "other",
]


class EmployeeCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    identification: str | None = Field(default=None, max_length=50)
    primary_phone: str | None = Field(default=None, max_length=50)
    secondary_phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    job_position: str | None = Field(default=None, max_length=120)
    employee_type: EmployeeType = "other"
    base_salary: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    payment_frequency: PaymentFrequency = "monthly"
    hire_date: date | None = None
    notes: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_required_names(cls, value: str) -> str:
        return _normalize_required_text(value, "Los nombres y apellidos son obligatorios.")

    @field_validator(
        "identification",
        "primary_phone",
        "secondary_phone",
        "address",
        "job_position",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    identification: str | None = Field(default=None, max_length=50)
    primary_phone: str | None = Field(default=None, max_length=50)
    secondary_phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    job_position: str | None = Field(default=None, max_length=120)
    employee_type: EmployeeType | None = None
    base_salary: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    payment_frequency: PaymentFrequency | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    notes: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_required_names(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(value, "Los nombres y apellidos son obligatorios.")

    @field_validator(
        "identification",
        "primary_phone",
        "secondary_phone",
        "address",
        "job_position",
        "notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "employee_type": self.employee_type,
            "base_salary": self.base_salary,
            "payment_frequency": self.payment_frequency,
        }
        for field_name, value in required_fields.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class EmployeeDeactivate(BaseModel):
    termination_date: date | None = None


class EmployeeRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    identification: str | None
    primary_phone: str | None
    secondary_phone: str | None
    address: str | None
    job_position: str | None
    employee_type: EmployeeType
    base_salary: Decimal
    payment_frequency: PaymentFrequency
    hire_date: date | None
    termination_date: date | None
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
