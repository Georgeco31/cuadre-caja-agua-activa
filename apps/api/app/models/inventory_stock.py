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


class InventoryStock(Base):
    __tablename__ = "inventory_stocks"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "location_id",
            name="uq_inventory_stocks_product_location",
        ),
        CheckConstraint(
            "quantity_on_hand >= 0",
            name="ck_inventory_stocks_quantity_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_locations.id"),
        nullable=False,
        index=True,
    )
    quantity_on_hand: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
        server_default="0.000",
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

    product: Mapped["Product"] = relationship("Product")
    location: Mapped["InventoryLocation"] = relationship("InventoryLocation")

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def product_sku(self) -> str | None:
        return self.product.sku

    @property
    def product_presentation(self) -> str | None:
        return self.product.presentation

    @property
    def location_name(self) -> str:
        return self.location.name

