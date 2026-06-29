from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CorrectionLog(Base):
    __tablename__ = "correction_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    cash_session_id: Mapped[int] = mapped_column(
        ForeignKey("cash_sessions.id"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    previous_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    new_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    cash_session: Mapped["CashSession"] = relationship(
        "CashSession",
        back_populates="correction_logs",
    )
    creator: Mapped["User | None"] = relationship(
        "User",
        back_populates="correction_logs",
    )
