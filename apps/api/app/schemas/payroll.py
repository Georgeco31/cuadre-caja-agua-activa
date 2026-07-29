from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PayrollStatus = Literal["draft", "approved", "paid", "cancelled"]
ZERO_MONEY = Decimal("0.00")


class PayrollLoanDeductionInput(BaseModel):
    employee_loan_id: int = Field(gt=0)
    amount_deducted: Decimal = Field(
        gt=ZERO_MONEY,
        max_digits=14,
        decimal_places=2,
    )


class PayrollItemValues(BaseModel):
    base_salary_amount: Decimal | None = Field(
        default=None,
        ge=ZERO_MONEY,
        max_digits=14,
        decimal_places=2,
    )
    bonus_amount: Decimal = Field(
        default=ZERO_MONEY,
        ge=ZERO_MONEY,
        max_digits=14,
        decimal_places=2,
    )
    other_income_amount: Decimal = Field(
        default=ZERO_MONEY,
        ge=ZERO_MONEY,
        max_digits=14,
        decimal_places=2,
    )
    other_deductions_amount: Decimal = Field(
        default=ZERO_MONEY,
        ge=ZERO_MONEY,
        max_digits=14,
        decimal_places=2,
    )
    advance_ids: list[int] = Field(default_factory=list)
    loan_deductions: list[PayrollLoanDeductionInput] = Field(
        default_factory=list,
    )
    notes: str | None = None

    @field_validator("advance_ids")
    @classmethod
    def validate_advance_ids(cls, value: list[int]) -> list[int]:
        if any(advance_id <= 0 for advance_id in value):
            raise ValueError("Los anticipos seleccionados no son válidos.")
        if len(value) != len(set(value)):
            raise ValueError("No se puede repetir un anticipo en el empleado.")
        return value

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_unique_loans(self):
        loan_ids = [
            deduction.employee_loan_id for deduction in self.loan_deductions
        ]
        if len(loan_ids) != len(set(loan_ids)):
            raise ValueError("No se puede repetir un préstamo en el empleado.")
        return self


class PayrollItemInput(PayrollItemValues):
    employee_id: int = Field(gt=0)


class PayrollItemUpdate(PayrollItemValues):
    correction_reason: str = Field(min_length=3)

    @field_validator("correction_reason")
    @classmethod
    def validate_correction_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo de corrección es obligatorio.",
        )


class PayrollCalculationRequest(BaseModel):
    period_start: date
    period_end: date
    employee_ids: list[int] = Field(default_factory=list)
    items: list[PayrollItemInput] = Field(default_factory=list)

    @field_validator("employee_ids")
    @classmethod
    def validate_employee_ids(cls, value: list[int]) -> list[int]:
        if any(employee_id <= 0 for employee_id in value):
            raise ValueError("Los empleados seleccionados no son válidos.")
        if len(value) != len(set(value)):
            raise ValueError("No se puede repetir un empleado en el rol.")
        return value

    @model_validator(mode="after")
    def validate_request(self):
        _validate_period(self.period_start, self.period_end)
        _validate_employee_selection(self.employee_ids, self.items)
        if not self.employee_ids and not self.items:
            raise ValueError("El rol debe tener al menos un empleado.")
        return self


class PayrollPreviewRequest(PayrollCalculationRequest):
    pass


class PayrollRunCreate(BaseModel):
    period_start: date
    period_end: date
    label: str = Field(min_length=1, max_length=160)
    payroll_date: date | None = None
    notes: str | None = None
    employee_ids: list[int] = Field(default_factory=list)
    items: list[PayrollItemInput] = Field(default_factory=list)

    @field_validator("label")
    @classmethod
    def normalize_label(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "La etiqueta del período es obligatoria.",
        )

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("employee_ids")
    @classmethod
    def validate_employee_ids(cls, value: list[int]) -> list[int]:
        if any(employee_id <= 0 for employee_id in value):
            raise ValueError("Los empleados seleccionados no son válidos.")
        if len(value) != len(set(value)):
            raise ValueError("No se puede repetir un empleado en el rol.")
        return value

    @model_validator(mode="after")
    def validate_request(self):
        _validate_period(self.period_start, self.period_end)
        _validate_employee_selection(self.employee_ids, self.items)
        return self


class PayrollCancel(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _normalize_required_text(
            value,
            "El motivo de cancelación es obligatorio.",
        )


class PayrollAdvanceDeductionCalculation(BaseModel):
    employee_advance_id: int
    amount_deducted: Decimal
    advance_number_snapshot: str
    advance_date_snapshot: date
    reason_snapshot: str


class PayrollLoanDeductionCalculation(BaseModel):
    employee_loan_id: int
    amount_deducted: Decimal
    loan_number_snapshot: str
    loan_date_snapshot: date
    loan_balance_snapshot: Decimal
    reason_snapshot: str


class PayrollItemCalculation(BaseModel):
    employee_id: int
    employee_name_snapshot: str
    employee_identification_snapshot: str | None
    job_position_snapshot: str | None
    payment_frequency_snapshot: str
    base_salary_snapshot: Decimal
    attendance_days: int
    absent_days: int
    permission_days: int
    vacation_days: int
    sick_days: int
    late_days: int
    hours_worked: Decimal
    base_salary_amount: Decimal
    bonus_amount: Decimal
    other_income_amount: Decimal
    gross_amount: Decimal
    advances_deducted_amount: Decimal
    loan_deductions_amount: Decimal
    other_deductions_amount: Decimal
    total_deductions_amount: Decimal
    net_pay_amount: Decimal
    notes: str | None
    advance_deductions: list[PayrollAdvanceDeductionCalculation]
    loan_deductions: list[PayrollLoanDeductionCalculation]


class PayrollPreviewRead(BaseModel):
    period_start: date
    period_end: date
    employees_count: int
    gross_total: Decimal
    bonuses_total: Decimal
    advances_deducted_total: Decimal
    loan_deductions_total: Decimal
    other_deductions_total: Decimal
    total_deductions: Decimal
    net_pay_total: Decimal
    items: list[PayrollItemCalculation]


class PayrollAdvanceDeductionRead(PayrollAdvanceDeductionCalculation):
    id: int
    payroll_item_id: int
    applied_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PayrollLoanDeductionRead(PayrollLoanDeductionCalculation):
    id: int
    payroll_item_id: int
    loan_payment_id: int | None
    applied_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PayrollItemRead(BaseModel):
    id: int
    payroll_run_id: int
    employee_id: int
    employee_name_snapshot: str
    employee_identification_snapshot: str | None
    job_position_snapshot: str | None
    payment_frequency_snapshot: str
    base_salary_snapshot: Decimal
    attendance_days: int
    absent_days: int
    permission_days: int
    vacation_days: int
    sick_days: int
    late_days: int
    hours_worked: Decimal
    base_salary_amount: Decimal
    bonus_amount: Decimal
    other_income_amount: Decimal
    gross_amount: Decimal
    advances_deducted_amount: Decimal
    loan_deductions_amount: Decimal
    other_deductions_amount: Decimal
    total_deductions_amount: Decimal
    net_pay_amount: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    advance_deductions: list[PayrollAdvanceDeductionRead]
    loan_deductions: list[PayrollLoanDeductionRead]

    model_config = ConfigDict(from_attributes=True)


class PayrollAuditRead(BaseModel):
    id: int
    payroll_run_id: int
    action: str
    actor_id: int
    reason: str | None
    details: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PayrollRunSummaryRead(BaseModel):
    id: int
    payroll_number: str
    label: str
    period_start: date
    period_end: date
    payroll_date: date
    status: PayrollStatus
    employees_count: int
    gross_total: Decimal
    bonuses_total: Decimal
    advances_deducted_total: Decimal
    loan_deductions_total: Decimal
    other_deductions_total: Decimal
    total_deductions: Decimal
    net_pay_total: Decimal
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    approved_by: int | None
    approved_at: datetime | None
    paid_by: int | None
    paid_at: datetime | None
    cancelled_by: int | None
    cancelled_at: datetime | None
    cancellation_reason: str | None

    model_config = ConfigDict(from_attributes=True)


class PayrollRunRead(PayrollRunSummaryRead):
    items: list[PayrollItemRead]
    audit_logs: list[PayrollAuditRead]


class EmployeePayrollAdvanceSummary(BaseModel):
    id: int
    advance_number: str
    advance_date: date
    amount: Decimal
    reserved_amount: Decimal
    estimated_balance: Decimal
    available_for_payroll: bool


class EmployeePayrollLoanSummary(BaseModel):
    id: int
    loan_number: str
    loan_date: date
    principal_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    reserved_amount: Decimal
    estimated_balance: Decimal
    available_for_payroll: bool


class EmployeePayrollSummary(BaseModel):
    employee_id: int
    employee_name: str
    base_salary: Decimal
    active_advances_total: Decimal
    active_loans_balance_total: Decimal
    reserved_advances_total: Decimal
    reserved_loans_total: Decimal
    estimated_pending_balance_after_reserved: Decimal
    advances: list[EmployeePayrollAdvanceSummary]
    loans: list[EmployeePayrollLoanSummary]
    paid_payroll_runs_count: int
    gross_paid_total: Decimal
    advances_deducted_total: Decimal
    loan_deductions_total: Decimal
    other_deductions_total: Decimal
    net_paid_total: Decimal
    latest_paid_payroll_items: list[PayrollItemRead]


def _validate_period(period_start: date, period_end: date) -> None:
    if period_end < period_start:
        raise ValueError(
            "La fecha final no puede ser menor que la fecha inicial.",
        )


def _validate_employee_selection(
    employee_ids: list[int],
    items: list[PayrollItemInput],
) -> None:
    item_employee_ids = [item.employee_id for item in items]
    if len(item_employee_ids) != len(set(item_employee_ids)):
        raise ValueError("No se puede repetir un empleado en el rol.")
    if employee_ids and any(
        employee_id not in employee_ids for employee_id in item_employee_ids
    ):
        raise ValueError(
            "Los ítems deben corresponder a empleados seleccionados.",
        )


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
