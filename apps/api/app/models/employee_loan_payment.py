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
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeLoanPayment(Base):
    __tablename__ = "employee_loan_payments"
    __table_args__ = (
        CheckConstraint(
            "length(trim(payment_number)) > 0",
            name="ck_employee_loan_payments_number_not_blank",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_employee_loan_payments_amount_positive",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_employee_loan_payments_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_employee_loan_payments_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    employee_loan_id: Mapped[int] = mapped_column(
        ForeignKey("employee_loans.id"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
    void_reason: Mapped[str | None] = mapped_column(Text)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
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

    loan: Mapped["EmployeeLoan"] = relationship(
        "EmployeeLoan",
        back_populates="payments",
    )
    employee: Mapped["Employee"] = relationship("Employee")
    creator: Mapped["User"] = relationship("User")

    @property
    def employee_name(self) -> str:
        return f"{self.employee.first_name} {self.employee.last_name}"

    @property
    def loan_number(self) -> str:
        return self.loan.loan_number
