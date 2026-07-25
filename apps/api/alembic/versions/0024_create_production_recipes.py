"""create production recipes and product classification

Revision ID: 0024_recipes
Revises: 0023_payroll
Create Date: 2026-07-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0024_recipes"
down_revision: str | None = "0023_payroll"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "product_kind",
            sa.String(length=30),
            server_default=sa.text("'finished_good'"),
            nullable=False,
        ),
    )
    op.add_column(
        "products",
        sa.Column("production_notes", sa.Text(), nullable=True),
    )
    op.create_check_constraint(
        "ck_products_product_kind",
        "products",
        "product_kind IN "
        "('finished_good', 'raw_material', 'supply', 'packaging', "
        "'service', 'other')",
    )
    op.create_index(
        "ix_products_product_kind",
        "products",
        ["product_kind"],
    )

    op.create_table(
        "production_recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_number", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("output_product_id", sa.Integer(), nullable=False),
        sa.Column("output_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'inactive'"),
            nullable=False,
        ),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column(
            "estimated_material_cost",
            sa.Numeric(16, 4),
            server_default=sa.text("'0.0000'"),
            nullable=False,
        ),
        sa.Column(
            "estimated_cost_per_unit",
            sa.Numeric(16, 4),
            server_default=sa.text("'0.0000'"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("void_reason", sa.Text(), nullable=True),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(recipe_number)) > 0",
            name="ck_production_recipes_number_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_production_recipes_name_not_blank",
        ),
        sa.CheckConstraint(
            "output_quantity > 0",
            name="ck_production_recipes_output_quantity_positive",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'voided')",
            name="ck_production_recipes_status",
        ),
        sa.CheckConstraint(
            "valid_from IS NULL OR valid_to IS NULL OR valid_to >= valid_from",
            name="ck_production_recipes_valid_dates",
        ),
        sa.CheckConstraint(
            "estimated_material_cost >= 0 AND estimated_cost_per_unit >= 0",
            name="ck_production_recipes_costs_nonnegative",
        ),
        sa.CheckConstraint(
            "(status != 'voided' AND void_reason IS NULL AND voided_at IS NULL) "
            "OR (status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_recipes_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["output_product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_number"),
    )
    for index_name, column_name in (
        ("ix_production_recipes_recipe_number", "recipe_number"),
        ("ix_production_recipes_output_product_id", "output_product_id"),
        ("ix_production_recipes_status", "status"),
        ("ix_production_recipes_valid_from", "valid_from"),
        ("ix_production_recipes_valid_to", "valid_to"),
        ("ix_production_recipes_created_by", "created_by"),
    ):
        op.create_index(index_name, "production_recipes", [column_name])

    op.create_table(
        "production_recipe_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("input_product_id", sa.Integer(), nullable=False),
        sa.Column(
            "input_product_sku_snapshot",
            sa.String(length=80),
            nullable=True,
        ),
        sa.Column(
            "input_product_name_snapshot",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "input_product_kind_snapshot",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "input_product_presentation_snapshot",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column("quantity_required", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(16, 4), nullable=False),
        sa.Column("total_cost", sa.Numeric(16, 4), nullable=False),
        sa.Column(
            "waste_percentage",
            sa.Numeric(7, 3),
            server_default=sa.text("'0.000'"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(input_product_name_snapshot)) > 0",
            name="ck_production_recipe_items_name_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "input_product_kind_snapshot IN "
            "('finished_good', 'raw_material', 'supply', 'packaging', "
            "'service', 'other')",
            name="ck_production_recipe_items_kind_snapshot",
        ),
        sa.CheckConstraint(
            "quantity_required > 0",
            name="ck_production_recipe_items_quantity_positive",
        ),
        sa.CheckConstraint(
            "unit_cost >= 0 AND total_cost >= 0",
            name="ck_production_recipe_items_costs_nonnegative",
        ),
        sa.CheckConstraint(
            "waste_percentage >= 0",
            name="ck_production_recipe_items_waste_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["input_product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["production_recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_production_recipe_items_recipe_id",
        "production_recipe_items",
        ["recipe_id"],
    )
    op.create_index(
        "ix_production_recipe_items_input_product_id",
        "production_recipe_items",
        ["input_product_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_production_recipe_items_input_product_id",
        table_name="production_recipe_items",
    )
    op.drop_index(
        "ix_production_recipe_items_recipe_id",
        table_name="production_recipe_items",
    )
    op.drop_table("production_recipe_items")
    for index_name in (
        "ix_production_recipes_created_by",
        "ix_production_recipes_valid_to",
        "ix_production_recipes_valid_from",
        "ix_production_recipes_status",
        "ix_production_recipes_output_product_id",
        "ix_production_recipes_recipe_number",
    ):
        op.drop_index(index_name, table_name="production_recipes")
    op.drop_table("production_recipes")
    op.drop_index("ix_products_product_kind", table_name="products")
    op.drop_constraint(
        "ck_products_product_kind",
        "products",
        type_="check",
    )
    op.drop_column("products", "production_notes")
    op.drop_column("products", "product_kind")
