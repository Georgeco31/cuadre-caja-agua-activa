from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_suppliers_name_not_blank",
        ),
        CheckConstraint(
            "identification IS NULL OR length(trim(identification)) > 0",
            name="ck_suppliers_identification_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    identification: Mapped[str | None] = mapped_column(
        String(80),
        unique=True,
        index=True,
    )
    primary_phone: Mapped[str | None] = mapped_column(String(50))
    secondary_phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    contact_name: Mapped[str | None] = mapped_column(String(255))
    supplier_type: Mapped[str | None] = mapped_column(String(80), index=True)
    payment_terms: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text)
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

    purchases: Mapped[list["Purchase"]] = relationship(
        "Purchase",
        back_populates="supplier",
        order_by="Purchase.id",
    )
