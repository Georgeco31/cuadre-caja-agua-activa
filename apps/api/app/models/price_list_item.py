from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PriceListItem(Base):
    __tablename__ = "price_list_items"
    __table_args__ = (
        CheckConstraint(
            "unit_price >= 0",
            name="ck_price_list_items_price_nonnegative",
        ),
        CheckConstraint(
            "min_quantity > 0",
            name="ck_price_list_items_min_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    price_list_id: Mapped[int] = mapped_column(
        ForeignKey("price_lists.id"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        server_default="1.000",
    )
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

    price_list: Mapped["PriceList"] = relationship(
        "PriceList",
        back_populates="items",
    )
    product: Mapped["Product"] = relationship("Product")

    @property
    def product_name(self) -> str:
        return self.product.name

    @property
    def product_sku(self) -> str | None:
        return self.product.sku

    @property
    def product_presentation(self) -> str | None:
        return self.product.presentation
