from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionItem(Base):
    __tablename__ = "production_items"
    __table_args__ = (
        CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_production_items_product_snapshot_not_blank",
        ),
        CheckConstraint(
            "quantity_produced > 0",
            name="ck_production_items_quantity_produced_positive",
        ),
        CheckConstraint(
            "quantity_waste >= 0",
            name="ck_production_items_quantity_waste_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    product_sku_snapshot: Mapped[str | None] = mapped_column(String(80))
    product_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    product_presentation_snapshot: Mapped[str | None] = mapped_column(String(100))
    quantity_produced: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )
    quantity_waste: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
        server_default="0.000",
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    production_batch: Mapped["ProductionBatch"] = relationship(
        "ProductionBatch",
        back_populates="items",
    )
    product: Mapped["Product"] = relationship("Product")
