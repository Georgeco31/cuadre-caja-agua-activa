"""create production material consumptions

Revision ID: 0025_materials
Revises: 0024_recipes
Create Date: 2026-07-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0025_materials"
down_revision: str | None = "0024_recipes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "production_material_consumptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("consumption_number", sa.String(length=50), nullable=False),
        sa.Column("production_batch_id", sa.Integer(), nullable=False),
        sa.Column("source_location_id", sa.Integer(), nullable=False),
        sa.Column("movement_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column(
            "total_material_cost",
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
            "length(trim(consumption_number)) > 0",
            name="ck_production_material_consumptions_number_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_production_material_consumptions_status",
        ),
        sa.CheckConstraint(
            "total_material_cost >= 0",
            name="ck_production_material_consumptions_cost_nonnegative",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_material_consumptions_void_state",
        ),
        sa.ForeignKeyConstraint([("created_by")], [("users.id")]),
        sa.ForeignKeyConstraint(
            ["production_batch_id"],
            ["production_batches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_location_id"],
            ["inventory_locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("consumption_number"),
    )
    for index_name, column_name in (
        (
            "ix_production_material_consumptions_consumption_number",
            "consumption_number",
        ),
        (
            "ix_production_material_consumptions_production_batch_id",
            "production_batch_id",
        ),
        (
            "ix_production_material_consumptions_source_location_id",
            "source_location_id",
        ),
        ("ix_production_material_consumptions_movement_date", "movement_date"),
        ("ix_production_material_consumptions_status", "status"),
        ("ix_production_material_consumptions_created_by", "created_by"),
    ):
        op.create_index(
            index_name,
            "production_material_consumptions",
            [column_name],
        )
    op.create_index(
        "uq_production_material_consumptions_active_batch",
        "production_material_consumptions",
        ["production_batch_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "production_material_consumption_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("consumption_id", sa.Integer(), nullable=False),
        sa.Column("production_item_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("recipe_item_id", sa.Integer(), nullable=False),
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
        sa.Column(
            "recipe_number_snapshot",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "recipe_name_snapshot",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "quantity_required_base",
            sa.Numeric(14, 3),
            nullable=False,
        ),
        sa.Column("quantity_consumed", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(16, 4), nullable=False),
        sa.Column("total_cost", sa.Numeric(16, 4), nullable=False),
        sa.Column("inventory_movement_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(input_product_name_snapshot)) > 0",
            name="ck_production_material_consumption_items_name_not_blank",
        ),
        sa.CheckConstraint(
            "input_product_kind_snapshot IN "
            "('finished_good', 'raw_material', 'supply', 'packaging', "
            "'service', 'other')",
            name="ck_production_material_consumption_items_kind",
        ),
        sa.CheckConstraint(
            "length(trim(recipe_number_snapshot)) > 0 "
            "AND length(trim(recipe_name_snapshot)) > 0",
            name="ck_production_material_consumption_items_recipe_not_blank",
        ),
        sa.CheckConstraint(
            "quantity_required_base > 0 AND quantity_consumed > 0",
            name="ck_production_material_consumption_items_quantities_positive",
        ),
        sa.CheckConstraint(
            "unit_cost >= 0 AND total_cost >= 0",
            name="ck_production_material_consumption_items_costs_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["consumption_id"],
            ["production_material_consumptions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["production_item_id"],
            ["production_items.id"],
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["production_recipes.id"]),
        sa.ForeignKeyConstraint(
            ["recipe_item_id"],
            ["production_recipe_items.id"],
        ),
        sa.ForeignKeyConstraint(["input_product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(
            ["inventory_movement_id"],
            ["inventory_movements.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inventory_movement_id"),
        sa.UniqueConstraint(
            "consumption_id",
            "production_item_id",
            "recipe_item_id",
            name="uq_production_material_consumption_items_source",
        ),
    )
    for index_name, column_name in (
        (
            "ix_production_material_consumption_items_consumption_id",
            "consumption_id",
        ),
        (
            "ix_production_material_consumption_items_production_item_id",
            "production_item_id",
        ),
        (
            "ix_production_material_consumption_items_recipe_id",
            "recipe_id",
        ),
        (
            "ix_production_material_consumption_items_recipe_item_id",
            "recipe_item_id",
        ),
        (
            "ix_production_material_consumption_items_input_product_id",
            "input_product_id",
        ),
    ):
        op.create_index(
            index_name,
            "production_material_consumption_items",
            [column_name],
        )


def downgrade() -> None:
    for index_name in (
        "ix_production_material_consumption_items_input_product_id",
        "ix_production_material_consumption_items_recipe_item_id",
        "ix_production_material_consumption_items_recipe_id",
        "ix_production_material_consumption_items_production_item_id",
        "ix_production_material_consumption_items_consumption_id",
    ):
        op.drop_index(
            index_name,
            table_name="production_material_consumption_items",
        )
    op.drop_table("production_material_consumption_items")

    op.drop_index(
        "uq_production_material_consumptions_active_batch",
        table_name="production_material_consumptions",
    )
    for index_name in (
        "ix_production_material_consumptions_created_by",
        "ix_production_material_consumptions_status",
        "ix_production_material_consumptions_movement_date",
        "ix_production_material_consumptions_source_location_id",
        "ix_production_material_consumptions_production_batch_id",
        "ix_production_material_consumptions_consumption_number",
    ):
        op.drop_index(
            index_name,
            table_name="production_material_consumptions",
        )
    op.drop_table("production_material_consumptions")
