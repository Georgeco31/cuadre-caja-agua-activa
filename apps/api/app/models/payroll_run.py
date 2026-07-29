from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    __table_args__ = (
        CheckConstraint(
            "length(trim(payroll_number)) > 0",
            name="ck_payroll_runs_number_not_blank",
        ),
        CheckConstraint(
            "length(trim(label)) > 0",
            name="ck_payroll_runs_label_not_blank",
        ),
        CheckConstraint(
            "period_end >= period_start",
            name="ck_payroll_runs_period_valid",
        ),
        CheckConstraint(
            "status IN ('draft', 'approved', 'paid', 'cancelled')",
            name="ck_payroll_runs_status",
        ),
        CheckConstraint(
            "employees_count >= 0",
            name="ck_payroll_runs_employees_count_nonnegative",
        ),
        CheckConstraint(
            "gross_total >= 0 AND bonuses_total >= 0 "
            "AND advances_deducted_total >= 0 "
            "AND loan_deductions_total >= 0 "
            "AND other_deductions_total >= 0 "
            "AND total_deductions >= 0 AND net_pay_total >= 0",
            name="ck_payroll_runs_totals_nonnegative",
        ),
        CheckConstraint(
            "("
            "status = 'draft' "
            "AND approved_by IS NULL AND approved_at IS NULL "
            "AND paid_by IS NULL AND paid_at IS NULL "
            "AND cancelled_by IS NULL AND cancelled_at IS NULL "
            "AND cancellation_reason IS NULL"
            ") OR ("
            "status = 'approved' "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND paid_by IS NULL AND paid_at IS NULL "
            "AND cancelled_by IS NULL AND cancelled_at IS NULL "
            "AND cancellation_reason IS NULL"
            ") OR ("
            "status = 'paid' "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND paid_by IS NOT NULL AND paid_at IS NOT NULL "
            "AND cancelled_by IS NULL AND cancelled_at IS NULL "
            "AND cancellation_reason IS NULL"
            ") OR ("
            "status = 'cancelled' "
            "AND paid_by IS NULL AND paid_at IS NULL "
            "AND cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL "
            "AND length(trim(cancellation_reason)) > 0 "
            "AND ((approved_by IS NULL AND approved_at IS NULL) "
            "OR (approved_by IS NOT NULL AND approved_at IS NOT NULL))"
            ")",
            name="ck_payroll_runs_workflow_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payroll_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payroll_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="draft",
        index=True,
    )
    employees_count: Mapped[int] = mapped_column(Integer, nullable=False)
    gross_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    bonuses_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    advances_deducted_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    loan_deductions_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    other_deductions_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    total_deductions: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    net_pay_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
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

    items: Mapped[list["PayrollItem"]] = relationship(
        "PayrollItem",
        back_populates="payroll_run",
        order_by="PayrollItem.id",
    )
    audit_logs: Mapped[list["PayrollAuditLog"]] = relationship(
        "PayrollAuditLog",
        back_populates="payroll_run",
        order_by="PayrollAuditLog.id",
    )
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )
    approver: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[approved_by],
    )
    payer: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[paid_by],
    )
    canceller: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[cancelled_by],
    )
