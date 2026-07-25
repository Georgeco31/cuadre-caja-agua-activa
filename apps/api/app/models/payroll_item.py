from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PayrollItem(Base):
    __tablename__ = "payroll_items"
    __table_args__ = (
        UniqueConstraint(
            "payroll_run_id",
            "employee_id",
            name="uq_payroll_items_run_employee",
        ),
        CheckConstraint(
            "length(trim(employee_name_snapshot)) > 0",
            name="ck_payroll_items_employee_name_not_blank",
        ),
        CheckConstraint(
            "base_salary_snapshot >= 0 AND base_salary_amount >= 0 "
            "AND bonus_amount >= 0 AND other_income_amount >= 0 "
            "AND gross_amount >= 0 AND advances_deducted_amount >= 0 "
            "AND loan_deductions_amount >= 0 "
            "AND other_deductions_amount >= 0 "
            "AND total_deductions_amount >= 0 AND net_pay_amount >= 0",
            name="ck_payroll_items_amounts_nonnegative",
        ),
        CheckConstraint(
            "attendance_days >= 0 AND absent_days >= 0 "
            "AND permission_days >= 0 AND vacation_days >= 0 "
            "AND sick_days >= 0 AND late_days >= 0 AND hours_worked >= 0",
            name="ck_payroll_items_attendance_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payroll_run_id: Mapped[int] = mapped_column(
        ForeignKey("payroll_runs.id"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )
    employee_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    employee_identification_snapshot: Mapped[str | None] = mapped_column(
        String(50),
    )
    job_position_snapshot: Mapped[str | None] = mapped_column(String(120))
    payment_frequency_snapshot: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    base_salary_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    attendance_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    absent_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    permission_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    vacation_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    sick_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    late_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    hours_worked: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default="0.00",
    )
    base_salary_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    bonus_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    other_income_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    advances_deducted_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    loan_deductions_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    other_deductions_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    total_deductions_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    net_pay_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    payroll_run: Mapped["PayrollRun"] = relationship(
        "PayrollRun",
        back_populates="items",
    )
    employee: Mapped["Employee"] = relationship("Employee")
    advance_deductions: Mapped[list["PayrollItemAdvanceDeduction"]] = (
        relationship(
            "PayrollItemAdvanceDeduction",
            back_populates="payroll_item",
            order_by="PayrollItemAdvanceDeduction.id",
        )
    )
    loan_deductions: Mapped[list["PayrollItemLoanDeduction"]] = relationship(
        "PayrollItemLoanDeduction",
        back_populates="payroll_item",
        order_by="PayrollItemLoanDeduction.id",
    )
