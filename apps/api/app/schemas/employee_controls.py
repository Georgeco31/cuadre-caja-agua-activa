from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AttendanceStatus = Literal[
    "present",
    "absent",
    "late",
    "permission",
    "vacation",
    "sick",
]
EmployeeAdvanceStatus = Literal["active", "voided"]
EmployeeLoanStatus = Literal["active", "paid", "voided"]
EmployeeLoanPaymentStatus = Literal["active", "voided"]


class EmployeeAttendanceCreate(BaseModel):
    employee_id: int = Field(gt=0)
    attendance_date: date
    status: AttendanceStatus
    check_in_time: time | None = None
    check_out_time: time | None = None
    hours_worked: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=8,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class EmployeeAttendanceUpdate(BaseModel):
    attendance_date: date | None = None
    status: AttendanceStatus | None = None
    check_in_time: time | None = None
    check_out_time: time | None = None
    hours_worked: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=8,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for field_name in ("attendance_date", "status"):
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class EmployeeAttendanceRead(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    attendance_date: date
    status: AttendanceStatus
    check_in_time: time | None
    check_out_time: time | None
    hours_worked: Decimal | None
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeAdvanceCreate(BaseModel):
    employee_id: int = Field(gt=0)
    advance_date: date
    amount: Decimal = Field(
        gt=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    reason: str = Field(min_length=1)
    notes: str | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo del anticipo es obligatorio.",
        )

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class EmployeeAdvanceRead(BaseModel):
    id: int
    advance_number: str
    employee_id: int
    employee_name: str
    advance_date: date
    amount: Decimal
    reason: str
    status: EmployeeAdvanceStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeLoanCreate(BaseModel):
    employee_id: int = Field(gt=0)
    loan_date: date
    principal_amount: Decimal = Field(
        gt=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    reason: str = Field(min_length=1)
    notes: str | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo del prestamo es obligatorio.",
        )

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class EmployeeLoanRead(BaseModel):
    id: int
    loan_number: str
    employee_id: int
    employee_name: str
    loan_date: date
    principal_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    status: EmployeeLoanStatus
    reason: str
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeLoanPaymentCreate(BaseModel):
    payment_date: date
    amount: Decimal = Field(
        gt=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class EmployeeLoanPaymentRead(BaseModel):
    id: int
    payment_number: str
    employee_loan_id: int
    loan_number: str
    employee_id: int
    employee_name: str
    payment_date: date
    amount: Decimal
    notes: str | None
    status: EmployeeLoanPaymentStatus
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeControlVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo de anulacion es obligatorio.",
        )


class EmployeeAccountSummary(BaseModel):
    employee_id: int
    employee_name: str
    advances_total_active: Decimal
    loans_principal_total: Decimal
    loans_paid_total: Decimal
    loans_balance_total: Decimal
    active_loans_count: int
    paid_loans_count: int
    attendance_count_period: int
    latest_advances: list[EmployeeAdvanceRead]
    latest_loans: list[EmployeeLoanRead]
    latest_loan_payments: list[EmployeeLoanPaymentRead]


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
