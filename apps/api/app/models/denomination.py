from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Denomination(Base):
    __tablename__ = "denominations"
    __table_args__ = (
        CheckConstraint(
            "type IN ('coin', 'bill')",
            name="ck_denominations_type",
        ),
        CheckConstraint("value > 0", name="ck_denominations_value_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    label: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    cash_count_items: Mapped[list["CashCountItem"]] = relationship(
        "CashCountItem",
        back_populates="denomination",
    )
