from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CashCountItem(Base):
    __tablename__ = "cash_count_items"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_cash_count_items_quantity_nonnegative"),
        CheckConstraint("subtotal >= 0", name="ck_cash_count_items_subtotal_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cash_session_id: Mapped[int] = mapped_column(
        ForeignKey("cash_sessions.id"),
        nullable=False,
    )
    denomination_id: Mapped[int] = mapped_column(
        ForeignKey("denominations.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    cash_session: Mapped["CashSession"] = relationship(
        "CashSession",
        back_populates="cash_count_items",
    )
    denomination: Mapped["Denomination"] = relationship(
        "Denomination",
        back_populates="cash_count_items",
    )
