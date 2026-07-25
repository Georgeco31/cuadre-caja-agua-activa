from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.supplier import SupplierRead

OperatingExpenseStatus = Literal["active", "voided"]
OperatingExpensePaymentStatus = Literal["unpaid", "paid", "partial"]
OperatingExpensePaymentMethod = Literal[
    "cash",
    "transfer",
    "card",
    "check",
    "other",
    "unknown",
]
RecurringOperatingExpenseFrequency = Literal[
    "weekly",
    "monthly",
    "quarterly",
    "yearly",
]


class OperatingExpenseCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El nombre de la categoria es obligatorio.",
        )

    @field_validator("description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class OperatingExpenseCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(
            value,
            "El nombre de la categoria es obligatorio.",
        )

    @field_validator("description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_name(self):
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("El nombre de la categoria no puede ser nulo.")
        return self


class OperatingExpenseCategoryRead(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperatingExpenseCreate(BaseModel):
    expense_date: date
    category_id: int = Field(gt=0)
    supplier_id: int | None = Field(default=None, gt=0)
    description: str = Field(min_length=1)
    amount: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )
    payment_status: OperatingExpensePaymentStatus = "unpaid"
    payment_method: OperatingExpensePaymentMethod = "unknown"
    document_number: str | None = Field(default=None, max_length=120)
    due_date: date | None = None
    paid_date: date | None = None
    notes: str | None = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "La descripcion del gasto es obligatoria.",
        )

    @field_validator("document_number", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class OperatingExpenseUpdate(BaseModel):
    expense_date: date | None = None
    category_id: int | None = Field(default=None, gt=0)
    supplier_id: int | None = Field(default=None, gt=0)
    description: str | None = None
    amount: Decimal | None = Field(
        default=None,
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )
    payment_status: OperatingExpensePaymentStatus | None = None
    payment_method: OperatingExpensePaymentMethod | None = None
    document_number: str | None = Field(default=None, max_length=120)
    due_date: date | None = None
    paid_date: date | None = None
    notes: str | None = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(
            value,
            "La descripcion del gasto es obligatoria.",
        )

    @field_validator("document_number", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = (
            "expense_date",
            "category_id",
            "description",
            "amount",
            "payment_status",
            "payment_method",
        )
        for field_name in required_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class OperatingExpenseVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo de anulacion es obligatorio.",
        )


class OperatingExpenseRead(BaseModel):
    id: int
    expense_number: str
    expense_date: date
    category_id: int
    supplier_id: int | None
    description: str
    amount: Decimal
    payment_status: OperatingExpensePaymentStatus
    payment_method: OperatingExpensePaymentMethod
    document_number: str | None
    due_date: date | None
    paid_date: date | None
    recurring_template_id: int | None
    status: OperatingExpenseStatus
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    category: OperatingExpenseCategoryRead
    supplier: SupplierRead | None

    model_config = ConfigDict(from_attributes=True)


class RecurringOperatingExpenseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category_id: int = Field(gt=0)
    supplier_id: int | None = Field(default=None, gt=0)
    description: str = Field(min_length=1)
    amount: Decimal = Field(
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )
    frequency: RecurringOperatingExpenseFrequency
    start_date: date
    end_date: date | None = None
    next_due_date: date | None = None
    payment_method: OperatingExpensePaymentMethod = "unknown"
    notes: str | None = None

    @field_validator("name", "description")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return _normalize_required_text(value, "El texto es obligatorio.")

    @field_validator("notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_dates(self):
        _validate_recurring_dates(
            self.start_date,
            self.end_date,
            self.next_due_date,
        )
        return self


class RecurringOperatingExpenseUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    category_id: int | None = Field(default=None, gt=0)
    supplier_id: int | None = Field(default=None, gt=0)
    description: str | None = None
    amount: Decimal | None = Field(
        default=None,
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=2,
    )
    frequency: RecurringOperatingExpenseFrequency | None = None
    start_date: date | None = None
    end_date: date | None = None
    next_due_date: date | None = None
    payment_method: OperatingExpensePaymentMethod | None = None
    notes: str | None = None

    @field_validator("name", "description")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(value, "El texto es obligatorio.")

    @field_validator("notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = (
            "name",
            "category_id",
            "description",
            "amount",
            "frequency",
            "start_date",
            "payment_method",
        )
        for field_name in required_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class RecurringOperatingExpenseRead(BaseModel):
    id: int
    name: str
    category_id: int
    supplier_id: int | None
    description: str
    amount: Decimal
    frequency: RecurringOperatingExpenseFrequency
    start_date: date
    end_date: date | None
    next_due_date: date | None
    payment_method: OperatingExpensePaymentMethod
    is_active: bool
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    category: OperatingExpenseCategoryRead
    supplier: SupplierRead | None

    model_config = ConfigDict(from_attributes=True)


class RecurringOperatingExpenseCreateExpense(BaseModel):
    expense_date: date
    due_date: date | None = None
    paid_date: date | None = None
    payment_status: OperatingExpensePaymentStatus = "unpaid"
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class OperatingExpenseSummaryCategory(BaseModel):
    category_id: int
    category_name: str
    total_amount: Decimal
    expenses_count: int


class OperatingExpenseSummarySupplier(BaseModel):
    supplier_id: int | None
    supplier_name: str
    total_amount: Decimal
    expenses_count: int


class OperatingExpenseSummaryPaymentStatus(BaseModel):
    payment_status: OperatingExpensePaymentStatus
    total_amount: Decimal
    expenses_count: int


class OperatingExpenseSummary(BaseModel):
    total_expenses_amount: Decimal
    paid_amount: Decimal
    unpaid_amount: Decimal
    partial_amount: Decimal
    expenses_count: int
    voided_count: int
    by_category: list[OperatingExpenseSummaryCategory]
    by_supplier: list[OperatingExpenseSummarySupplier]
    by_payment_status: list[OperatingExpenseSummaryPaymentStatus]


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


def _validate_recurring_dates(
    start_date: date,
    end_date: date | None,
    next_due_date: date | None,
) -> None:
    if end_date is not None and start_date > end_date:
        raise ValueError(
            "La fecha de inicio no puede ser posterior a la fecha final.",
        )
    if next_due_date is not None and next_due_date < start_date:
        raise ValueError(
            "El proximo vencimiento no puede ser anterior al inicio.",
        )
    if (
        next_due_date is not None
        and end_date is not None
        and next_due_date > end_date
    ):
        raise ValueError(
            "El proximo vencimiento no puede ser posterior a la fecha final.",
        )
