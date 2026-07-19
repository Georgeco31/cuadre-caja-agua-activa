from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RouteLoadItem(Base):
    __tablename__ = "route_load_items"
    __table_args__ = (
        CheckConstraint(
            "quantity_loaded > 0",
            name="ck_route_load_items_quantity_positive",
        ),
        CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_route_load_items_product_snapshot_not_blank",
        ),
        UniqueConstraint(
            "route_load_id",
            "product_id",
            name="uq_route_load_items_product",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    route_load_id: Mapped[int] = mapped_column(
        ForeignKey("route_loads.id"),
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
    product_presentation_snapshot: Mapped[str | None] = mapped_column(String(255))
    quantity_loaded: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )
    source_exit_movement_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_movements.id"),
        nullable=False,
        unique=True,
    )
    destination_entry_movement_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_movements.id"),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    route_load: Mapped["RouteLoad"] = relationship(
        "RouteLoad",
        back_populates="items",
    )
    product: Mapped["Product"] = relationship("Product")
    source_exit_movement: Mapped["InventoryMovement"] = relationship(
        "InventoryMovement",
        foreign_keys=[source_exit_movement_id],
    )
    destination_entry_movement: Mapped["InventoryMovement"] = relationship(
        "InventoryMovement",
        foreign_keys=[destination_entry_movement_id],
    )

    @property
    def source_exit_movement_status(self) -> str:
        return self.source_exit_movement.status

    @property
    def destination_entry_movement_status(self) -> str:
        return self.destination_entry_movement.status
