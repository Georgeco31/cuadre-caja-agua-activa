from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionInventoryApplicationItem(Base):
    __tablename__ = "production_inventory_application_items"
    __table_args__ = (
        CheckConstraint(
            "quantity_applied > 0",
            name="ck_production_inventory_application_items_quantity_positive",
        ),
        UniqueConstraint(
            "application_id",
            "production_item_id",
            name="uq_production_inventory_application_items_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("production_inventory_applications.id"),
        nullable=False,
        index=True,
    )
    production_item_id: Mapped[int] = mapped_column(
        ForeignKey("production_items.id"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    inventory_movement_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_movements.id"),
        unique=True,
        nullable=False,
    )
    quantity_applied: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    application: Mapped["ProductionInventoryApplication"] = relationship(
        "ProductionInventoryApplication",
        back_populates="items",
    )
    production_item: Mapped["ProductionItem"] = relationship("ProductionItem")
    product: Mapped["Product"] = relationship("Product")
    inventory_movement: Mapped["InventoryMovement"] = relationship(
        "InventoryMovement",
    )
