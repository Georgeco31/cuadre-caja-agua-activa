from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionInventoryApplication(Base):
    __tablename__ = "production_inventory_applications"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_production_inventory_applications_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_inventory_applications_void_state",
        ),
        Index(
            "uq_production_inventory_applications_active_batch",
            "production_batch_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_locations.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
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

    production_batch: Mapped["ProductionBatch"] = relationship(
        "ProductionBatch",
        back_populates="inventory_applications",
    )
    location: Mapped["InventoryLocation"] = relationship("InventoryLocation")
    creator: Mapped["User"] = relationship("User")
    items: Mapped[list["ProductionInventoryApplicationItem"]] = relationship(
        "ProductionInventoryApplicationItem",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ProductionInventoryApplicationItem.id",
    )

    @property
    def location_name(self) -> str:
        return self.location.name
