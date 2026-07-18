"""create base inventory

Revision ID: 0011_inventory
Revises: 0010_payments
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0011_inventory"
down_revision: str | None = "0010_payments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inventory_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "location_type",
            sa.String(length=30),
            server_default=sa.text("'warehouse'"),
            nullable=False,
        ),
        sa.Column("vehicle_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
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
            "length(trim(name)) > 0",
            name="ck_inventory_locations_name_not_blank",
        ),
        sa.CheckConstraint(
            "location_type IN ('warehouse', 'vehicle', 'production_area', 'other')",
            name="ck_inventory_locations_type",
        ),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "inventory_stocks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column(
            "quantity_on_hand",
            sa.Numeric(precision=14, scale=3),
            server_default=sa.text("0.000"),
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
            "quantity_on_hand >= 0",
            name="ck_inventory_stocks_quantity_nonnegative",
        ),
        sa.ForeignKeyConstraint(["location_id"], ["inventory_locations.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "product_id",
            "location_id",
            name="uq_inventory_stocks_product_location",
        ),
    )
    op.create_index(
        "ix_inventory_stocks_location_id",
        "inventory_stocks",
        ["location_id"],
    )
    op.create_index(
        "ix_inventory_stocks_product_id",
        "inventory_stocks",
        ["product_id"],
    )

    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("movement_date", sa.Date(), nullable=False),
        sa.Column("movement_type", sa.String(length=30), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("product_sku_snapshot", sa.String(length=80), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column(
            "product_presentation_snapshot",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column(
            "unit_cost",
            sa.Numeric(precision=14, scale=2),
            nullable=True,
        ),
        sa.Column(
            "total_cost",
            sa.Numeric(precision=14, scale=2),
            nullable=True,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
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
            "movement_type IN ('entry', 'exit', 'adjustment_in', 'adjustment_out')",
            name="ck_inventory_movements_type",
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_inventory_movements_quantity_positive",
        ),
        sa.CheckConstraint(
            "unit_cost IS NULL OR unit_cost >= 0",
            name="ck_inventory_movements_unit_cost_nonnegative",
        ),
        sa.CheckConstraint(
            "total_cost IS NULL OR total_cost >= 0",
            name="ck_inventory_movements_total_cost_nonnegative",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_inventory_movements_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_inventory_movements_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["inventory_locations.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_inventory_movements_location_id",
        "inventory_movements",
        ["location_id"],
    )
    op.create_index(
        "ix_inventory_movements_movement_date",
        "inventory_movements",
        ["movement_date"],
    )
    op.create_index(
        "ix_inventory_movements_movement_type",
        "inventory_movements",
        ["movement_type"],
    )
    op.create_index(
        "ix_inventory_movements_product_id",
        "inventory_movements",
        ["product_id"],
    )
    op.create_index(
        "ix_inventory_movements_status",
        "inventory_movements",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_inventory_movements_status",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_product_id",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_movement_type",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_movement_date",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_location_id",
        table_name="inventory_movements",
    )
    op.drop_table("inventory_movements")
    op.drop_index(
        "ix_inventory_stocks_product_id",
        table_name="inventory_stocks",
    )
    op.drop_index(
        "ix_inventory_stocks_location_id",
        table_name="inventory_stocks",
    )
    op.drop_table("inventory_stocks")
    op.drop_table("inventory_locations")

