from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SaleDateCorrection(Base):
    __tablename__ = "sale_date_corrections"
    __table_args__ = (
        CheckConstraint(
            "correction_type = 'date_change'",
            name="ck_sale_date_corrections_type",
        ),
        CheckConstraint(
            "previous_sale_date <> new_sale_date",
            name="ck_sale_date_corrections_dates_different",
        ),
        CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_sale_date_corrections_reason_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id"),
        nullable=False,
        index=True,
    )
    correction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="date_change",
    )
    previous_sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    new_sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    sale: Mapped["Sale"] = relationship(
        "Sale",
        back_populates="date_corrections",
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="sale_date_corrections",
    )
