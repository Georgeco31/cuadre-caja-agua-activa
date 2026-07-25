from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionMaterialConsumption(Base):
    __tablename__ = "production_material_consumptions"
    __table_args__ = (
        CheckConstraint(
            "length(trim(consumption_number)) > 0",
            name="ck_production_material_consumptions_number_not_blank",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_production_material_consumptions_status",
        ),
        CheckConstraint(
            "total_material_cost >= 0",
            name="ck_production_material_consumptions_cost_nonnegative",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_material_consumptions_void_state",
        ),
        UniqueConstraint(
            "consumption_number",
        ),
        Index(
            "uq_production_material_consumptions_active_batch",
            "production_batch_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    consumption_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=False,
        index=True,
    )
    source_location_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_locations.id"),
        nullable=False,
        index=True,
    )
    movement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
    total_material_cost: Mapped[Decimal] = mapped_column(
        Numeric(16, 4),
        nullable=False,
        server_default="0.0000",
    )
    notes: Mapped[str | None] = mapped_column(Text)
    void_reason: Mapped[str | None] = mapped_column(Text)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    production_batch: Mapped["ProductionBatch"] = relationship(
        "ProductionBatch",
        back_populates="material_consumptions",
    )
    source_location: Mapped["InventoryLocation"] = relationship(
        "InventoryLocation",
    )
    creator: Mapped["User"] = relationship("User")
    items: Mapped[list["ProductionMaterialConsumptionItem"]] = relationship(
        "ProductionMaterialConsumptionItem",
        back_populates="consumption",
        cascade="all, delete-orphan",
        order_by="ProductionMaterialConsumptionItem.id",
    )

    @property
    def production_number(self) -> str:
        return self.production_batch.production_number

    @property
    def source_location_name(self) -> str:
        return self.source_location.name
