from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PayrollItemLoanDeduction(Base):
    __tablename__ = "payroll_item_loan_deductions"
    __table_args__ = (
        UniqueConstraint(
            "payroll_item_id",
            "employee_loan_id",
            name="uq_payroll_item_loan_deductions_item_loan",
        ),
        CheckConstraint(
            "amount_deducted > 0",
            name="ck_payroll_item_loan_deductions_amount_positive",
        ),
        CheckConstraint(
            "loan_balance_snapshot >= amount_deducted",
            name="ck_payroll_item_loan_deductions_within_balance",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payroll_item_id: Mapped[int] = mapped_column(
        ForeignKey("payroll_items.id"),
        nullable=False,
        index=True,
    )
    employee_loan_id: Mapped[int] = mapped_column(
        ForeignKey("employee_loans.id"),
        nullable=False,
        index=True,
    )
    amount_deducted: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    loan_number_snapshot: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    loan_date_snapshot: Mapped[date] = mapped_column(Date, nullable=False)
    loan_balance_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    reason_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    loan_payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee_loan_payments.id"),
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    payroll_item: Mapped["PayrollItem"] = relationship(
        "PayrollItem",
        back_populates="loan_deductions",
    )
    employee_loan: Mapped["EmployeeLoan"] = relationship("EmployeeLoan")
    loan_payment: Mapped["EmployeeLoanPayment | None"] = relationship(
        "EmployeeLoanPayment",
    )
