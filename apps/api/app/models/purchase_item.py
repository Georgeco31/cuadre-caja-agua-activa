from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    __table_args__ = (
        CheckConstraint(
            "product_id IS NOT NULL OR "
            "(description IS NOT NULL AND length(trim(description)) > 0)",
            name="ck_purchase_items_product_or_description",
        ),
        CheckConstraint(
            "product_id IS NULL OR "
            "(product_name_snapshot IS NOT NULL "
            "AND length(trim(product_name_snapshot)) > 0)",
            name="ck_purchase_items_product_snapshot",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_purchase_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_cost >= 0 AND discount_amount >= 0 AND tax_amount >= 0 "
            "AND subtotal_amount >= 0 AND total_amount >= 0",
            name="ck_purchase_items_amounts_nonnegative",
        ),
        CheckConstraint(
            "subtotal_amount = round(quantity * unit_cost - discount_amount, 2)",
            name="ck_purchase_items_subtotal",
        ),
        CheckConstraint(
            "total_amount = subtotal_amount + tax_amount",
            name="ck_purchase_items_total",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_id: Mapped[int] = mapped_column(
        ForeignKey("purchases.id"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"),
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text)
    product_sku_snapshot: Mapped[str | None] = mapped_column(String(80))
    product_name_snapshot: Mapped[str | None] = mapped_column(String(255))
    product_presentation_snapshot: Mapped[str | None] = mapped_column(String(100))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    purchase: Mapped["Purchase"] = relationship(
        "Purchase",
        back_populates="items",
    )
    product: Mapped["Product | None"] = relationship("Product")
