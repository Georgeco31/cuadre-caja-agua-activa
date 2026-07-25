from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionRecipeItem(Base):
    __tablename__ = "production_recipe_items"
    __table_args__ = (
        CheckConstraint(
            "length(trim(input_product_name_snapshot)) > 0",
            name="ck_production_recipe_items_name_snapshot_not_blank",
        ),
        CheckConstraint(
            "input_product_kind_snapshot IN "
            "('finished_good', 'raw_material', 'supply', 'packaging', "
            "'service', 'other')",
            name="ck_production_recipe_items_kind_snapshot",
        ),
        CheckConstraint(
            "quantity_required > 0",
            name="ck_production_recipe_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_cost >= 0 AND total_cost >= 0",
            name="ck_production_recipe_items_costs_nonnegative",
        ),
        CheckConstraint(
            "waste_percentage >= 0",
            name="ck_production_recipe_items_waste_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("production_recipes.id"),
        nullable=False,
        index=True,
    )
    input_product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    input_product_sku_snapshot: Mapped[str | None] = mapped_column(String(80))
    input_product_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    input_product_kind_snapshot: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    input_product_presentation_snapshot: Mapped[str | None] = mapped_column(
        String(100),
    )
    quantity_required: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(16, 4),
        nullable=False,
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(16, 4),
        nullable=False,
    )
    waste_percentage: Mapped[Decimal] = mapped_column(
        Numeric(7, 3),
        nullable=False,
        server_default="0.000",
    )
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
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

    recipe: Mapped["ProductionRecipe"] = relationship(
        "ProductionRecipe",
        back_populates="items",
    )
    input_product: Mapped["Product"] = relationship("Product")
