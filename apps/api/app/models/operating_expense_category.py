from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OperatingExpenseCategory(Base):
    __tablename__ = "operating_expense_categories"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_operating_expense_categories_name_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
        index=True,
    )
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

    expenses: Mapped[list["OperatingExpense"]] = relationship(
        "OperatingExpense",
        back_populates="category",
    )
    recurring_templates: Mapped[list["RecurringOperatingExpense"]] = (
        relationship(
            "RecurringOperatingExpense",
            back_populates="category",
        )
    )
