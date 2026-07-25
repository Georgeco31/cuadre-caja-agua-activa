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


class EmployeeLoan(Base):
    __tablename__ = "employee_loans"
    __table_args__ = (
        CheckConstraint(
            "length(trim(loan_number)) > 0",
            name="ck_employee_loans_number_not_blank",
        ),
        CheckConstraint(
            "principal_amount > 0",
            name="ck_employee_loans_principal_positive",
        ),
        CheckConstraint(
            "paid_amount >= 0 AND paid_amount <= principal_amount",
            name="ck_employee_loans_paid_valid",
        ),
        CheckConstraint(
            "balance_amount >= 0 AND "
            "balance_amount = principal_amount - paid_amount",
            name="ck_employee_loans_balance_valid",
        ),
        CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_employee_loans_reason_not_blank",
        ),
        CheckConstraint(
            "status IN ('active', 'paid', 'voided')",
            name="ck_employee_loans_status",
        ),
        CheckConstraint(
            "(status = 'paid' AND balance_amount = 0) OR "
            "(status = 'active' AND balance_amount > 0) OR "
            "status = 'voided'",
            name="ck_employee_loans_status_balance",
        ),
        CheckConstraint(
            "(status IN ('active', 'paid') AND void_reason IS NULL "
            "AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_employee_loans_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )
    loan_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    principal_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default="0.00",
    )
    balance_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
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

    employee: Mapped["Employee"] = relationship("Employee")
    payments: Mapped[list["EmployeeLoanPayment"]] = relationship(
        "EmployeeLoanPayment",
        back_populates="loan",
    )
    creator: Mapped["User"] = relationship("User")

    @property
    def employee_name(self) -> str:
        return f"{self.employee.first_name} {self.employee.last_name}"
