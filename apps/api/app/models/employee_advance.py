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


class EmployeeAdvance(Base):
    __tablename__ = "employee_advances"
    __table_args__ = (
        CheckConstraint(
            "length(trim(advance_number)) > 0",
            name="ck_employee_advances_number_not_blank",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_employee_advances_amount_positive",
        ),
        CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_employee_advances_reason_not_blank",
        ),
        CheckConstraint(
            "status IN ('active', 'deducted', 'voided')",
            name="ck_employee_advances_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL "
            "AND deducted_at IS NULL AND deducted_by IS NULL "
            "AND deducted_payroll_run_id IS NULL) OR "
            "(status = 'deducted' AND void_reason IS NULL "
            "AND voided_at IS NULL AND deducted_at IS NOT NULL "
            "AND deducted_by IS NOT NULL "
            "AND deducted_payroll_run_id IS NOT NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL AND deducted_at IS NULL "
            "AND deducted_by IS NULL AND deducted_payroll_run_id IS NULL)",
            name="ck_employee_advances_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    advance_number: Mapped[str] = mapped_column(
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
    advance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    void_reason: Mapped[str | None] = mapped_column(Text)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deducted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deducted_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    deducted_payroll_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("payroll_runs.id"),
        index=True,
    )
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
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )
    deductor: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[deducted_by],
    )

    @property
    def employee_name(self) -> str:
        return f"{self.employee.first_name} {self.employee.last_name}"
