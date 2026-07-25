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


class PayrollItemAdvanceDeduction(Base):
    __tablename__ = "payroll_item_advance_deductions"
    __table_args__ = (
        UniqueConstraint(
            "payroll_item_id",
            "employee_advance_id",
            name="uq_payroll_item_advance_deductions_item_advance",
        ),
        CheckConstraint(
            "amount_deducted > 0",
            name="ck_payroll_item_advance_deductions_amount_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payroll_item_id: Mapped[int] = mapped_column(
        ForeignKey("payroll_items.id"),
        nullable=False,
        index=True,
    )
    employee_advance_id: Mapped[int] = mapped_column(
        ForeignKey("employee_advances.id"),
        nullable=False,
        index=True,
    )
    amount_deducted: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    advance_number_snapshot: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    advance_date_snapshot: Mapped[date] = mapped_column(Date, nullable=False)
    reason_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    payroll_item: Mapped["PayrollItem"] = relationship(
        "PayrollItem",
        back_populates="advance_deductions",
    )
    employee_advance: Mapped["EmployeeAdvance"] = relationship(
        "EmployeeAdvance",
    )
