from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionRecipe(Base):
    __tablename__ = "production_recipes"
    __table_args__ = (
        CheckConstraint(
            "length(trim(recipe_number)) > 0",
            name="ck_production_recipes_number_not_blank",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_production_recipes_name_not_blank",
        ),
        CheckConstraint(
            "output_quantity > 0",
            name="ck_production_recipes_output_quantity_positive",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'voided')",
            name="ck_production_recipes_status",
        ),
        CheckConstraint(
            "valid_from IS NULL OR valid_to IS NULL OR valid_to >= valid_from",
            name="ck_production_recipes_valid_dates",
        ),
        CheckConstraint(
            "estimated_material_cost >= 0 AND estimated_cost_per_unit >= 0",
            name="ck_production_recipes_costs_nonnegative",
        ),
        CheckConstraint(
            "(status != 'voided' AND void_reason IS NULL AND voided_at IS NULL) "
            "OR (status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_recipes_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    output_product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    output_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="inactive",
        index=True,
    )
    valid_from: Mapped[date | None] = mapped_column(Date, index=True)
    valid_to: Mapped[date | None] = mapped_column(Date, index=True)
    estimated_material_cost: Mapped[Decimal] = mapped_column(
        Numeric(16, 4),
        nullable=False,
        server_default="0.0000",
    )
    estimated_cost_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4),
        nullable=False,
        server_default="0.0000",
    )
    notes: Mapped[str | None] = mapped_column(Text)
    void_reason: Mapped[str | None] = mapped_column(Text)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
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

    output_product: Mapped["Product"] = relationship("Product")
    creator: Mapped["User"] = relationship("User")
    items: Mapped[list["ProductionRecipeItem"]] = relationship(
        "ProductionRecipeItem",
        back_populates="recipe",
        order_by="ProductionRecipeItem.id",
    )

    @property
    def output_product_name(self) -> str:
        return self.output_product.name

    @property
    def output_product_kind(self) -> str:
        return self.output_product.product_kind
