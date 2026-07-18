from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Numeric,
    String,
    Text,
    false,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_products_name_not_blank",
        ),
        CheckConstraint(
            "category IN ('water', 'bottle', 'gallon', 'dispenser', 'container', 'other')",
            name="ck_products_category",
        ),
        CheckConstraint(
            "unit IN ('unit', 'pack', 'liter', 'gallon', 'bottle', 'container', 'other')",
            name="ck_products_unit",
        ),
        CheckConstraint(
            "default_price >= 0",
            name="ck_products_default_price_nonnegative",
        ),
        CheckConstraint(
            "cost_estimate >= 0",
            name="ck_products_cost_estimate_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str | None] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="other",
    )
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="unit",
    )
    presentation: Mapped[str | None] = mapped_column(String(100))
    default_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_estimate: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0.00",
    )
    is_returnable_container: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
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
