from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = (
        CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_sale_items_product_snapshot_not_blank",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_sale_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_sale_items_unit_price_nonnegative",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="ck_sale_items_subtotal_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_sku_snapshot: Mapped[str | None] = mapped_column(String(80))
    product_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    product_presentation_snapshot: Mapped[str | None] = mapped_column(String(100))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
