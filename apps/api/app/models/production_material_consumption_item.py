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


class ProductionMaterialConsumptionItem(Base):
    __tablename__ = "production_material_consumption_items"
    __table_args__ = (
        CheckConstraint(
            "length(trim(input_product_name_snapshot)) > 0",
            name="ck_production_material_consumption_items_name_not_blank",
        ),
        CheckConstraint(
            "input_product_kind_snapshot IN "
            "('finished_good', 'raw_material', 'supply', 'packaging', "
            "'service', 'other')",
            name="ck_production_material_consumption_items_kind",
        ),
        CheckConstraint(
            "length(trim(recipe_number_snapshot)) > 0 "
            "AND length(trim(recipe_name_snapshot)) > 0",
            name="ck_production_material_consumption_items_recipe_not_blank",
        ),
        CheckConstraint(
            "quantity_required_base > 0 AND quantity_consumed > 0",
            name="ck_production_material_consumption_items_quantities_positive",
        ),
        CheckConstraint(
            "unit_cost >= 0 AND total_cost >= 0",
            name="ck_production_material_consumption_items_costs_nonnegative",
        ),
        UniqueConstraint(
            "consumption_id",
            "production_item_id",
            "recipe_item_id",
            name="uq_production_material_consumption_items_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    consumption_id: Mapped[int] = mapped_column(
        ForeignKey("production_material_consumptions.id"),
        nullable=False,
        index=True,
    )
    production_item_id: Mapped[int] = mapped_column(
        ForeignKey("production_items.id"),
        nullable=False,
        index=True,
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("production_recipes.id"),
        nullable=False,
        index=True,
    )
    recipe_item_id: Mapped[int] = mapped_column(
        ForeignKey("production_recipe_items.id"),
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
    recipe_number_snapshot: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    recipe_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    quantity_required_base: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )
    quantity_consumed: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    inventory_movement_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_movements.id"),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    consumption: Mapped["ProductionMaterialConsumption"] = relationship(
        "ProductionMaterialConsumption",
        back_populates="items",
    )
    production_item: Mapped["ProductionItem"] = relationship("ProductionItem")
    recipe: Mapped["ProductionRecipe"] = relationship("ProductionRecipe")
    recipe_item: Mapped["ProductionRecipeItem"] = relationship(
        "ProductionRecipeItem",
    )
    input_product: Mapped["Product"] = relationship("Product")
    inventory_movement: Mapped["InventoryMovement"] = relationship(
        "InventoryMovement",
    )
