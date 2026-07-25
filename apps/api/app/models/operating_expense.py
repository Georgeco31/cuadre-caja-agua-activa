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


class OperatingExpense(Base):
    __tablename__ = "operating_expenses"
    __table_args__ = (
        CheckConstraint(
            "length(trim(expense_number)) > 0",
            name="ck_operating_expenses_number_not_blank",
        ),
        CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_operating_expenses_description_not_blank",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_operating_expenses_amount_positive",
        ),
        CheckConstraint(
            "payment_status IN ('unpaid', 'paid', 'partial')",
            name="ck_operating_expenses_payment_status",
        ),
        CheckConstraint(
            "payment_method IN "
            "('cash', 'transfer', 'card', 'check', 'other', 'unknown')",
            name="ck_operating_expenses_payment_method",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_operating_expenses_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_operating_expenses_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("operating_expense_categories.id"),
        nullable=False,
        index=True,
    )
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id"),
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="unpaid",
        index=True,
    )
    payment_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="unknown",
        index=True,
    )
    document_number: Mapped[str | None] = mapped_column(
        String(120),
        index=True,
    )
    due_date: Mapped[date | None] = mapped_column(Date, index=True)
    paid_date: Mapped[date | None] = mapped_column(Date, index=True)
    recurring_template_id: Mapped[int | None] = mapped_column(
        ForeignKey("recurring_operating_expenses.id"),
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
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

    category: Mapped["OperatingExpenseCategory"] = relationship(
        "OperatingExpenseCategory",
        back_populates="expenses",
    )
    supplier: Mapped["Supplier | None"] = relationship("Supplier")
    recurring_template: Mapped["RecurringOperatingExpense | None"] = relationship(
        "RecurringOperatingExpense",
        back_populates="expenses",
    )
    creator: Mapped["User"] = relationship("User")
