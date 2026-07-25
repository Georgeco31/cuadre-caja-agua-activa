from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecurringOperatingExpense(Base):
    __tablename__ = "recurring_operating_expenses"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_recurring_operating_expenses_name_not_blank",
        ),
        CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_recurring_operating_expenses_description_not_blank",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_recurring_operating_expenses_amount_positive",
        ),
        CheckConstraint(
            "frequency IN ('weekly', 'monthly', 'quarterly', 'yearly')",
            name="ck_recurring_operating_expenses_frequency",
        ),
        CheckConstraint(
            "payment_method IN "
            "('cash', 'transfer', 'card', 'check', 'other', 'unknown')",
            name="ck_recurring_operating_expenses_payment_method",
        ),
        CheckConstraint(
            "end_date IS NULL OR start_date <= end_date",
            name="ck_recurring_operating_expenses_date_range",
        ),
        CheckConstraint(
            "next_due_date IS NULL OR next_due_date >= start_date",
            name="ck_recurring_operating_expenses_next_due_after_start",
        ),
        CheckConstraint(
            "next_due_date IS NULL OR end_date IS NULL "
            "OR next_due_date <= end_date",
            name="ck_recurring_operating_expenses_next_due_before_end",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
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
    frequency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date | None] = mapped_column(Date)
    next_due_date: Mapped[date | None] = mapped_column(Date, index=True)
    payment_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="unknown",
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text)
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
        back_populates="recurring_templates",
    )
    supplier: Mapped["Supplier | None"] = relationship("Supplier")
    creator: Mapped["User"] = relationship("User")
    expenses: Mapped[list["OperatingExpense"]] = relationship(
        "OperatingExpense",
        back_populates="recurring_template",
    )
