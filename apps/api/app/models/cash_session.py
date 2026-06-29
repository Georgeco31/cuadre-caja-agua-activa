from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CashSession(Base):
    __tablename__ = "cash_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'closed', 'corrected')",
            name="ck_cash_sessions_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="open",
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
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
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    creator: Mapped["User | None"] = relationship(
        "User",
        back_populates="cash_sessions",
    )
    cash_count_items: Mapped[list["CashCountItem"]] = relationship(
        "CashCountItem",
        back_populates="cash_session",
    )
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="cash_session",
    )
    correction_logs: Mapped[list["CorrectionLog"]] = relationship(
        "CorrectionLog",
        back_populates="cash_session",
    )
