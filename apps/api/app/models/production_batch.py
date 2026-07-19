from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionBatch(Base):
    __tablename__ = "production_batches"
    __table_args__ = (
        CheckConstraint(
            "length(trim(production_number)) > 0",
            name="ck_production_batches_number_not_blank",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_production_batches_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_batches_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    production_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    production_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
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

    creator: Mapped["User"] = relationship("User")
    items: Mapped[list["ProductionItem"]] = relationship(
        "ProductionItem",
        back_populates="production_batch",
        cascade="all, delete-orphan",
        order_by="ProductionItem.id",
    )
    inventory_applications: Mapped[
        list["ProductionInventoryApplication"]
    ] = relationship(
        "ProductionInventoryApplication",
        back_populates="production_batch",
        order_by="ProductionInventoryApplication.id",
    )
