"""create route loads

Revision ID: 0014_route_loads
Revises: 0013_prod_inventory
Create Date: 2026-07-19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0014_route_loads"
down_revision: str | None = "0013_prod_inventory"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "route_loads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("load_number", sa.String(length=80), nullable=False),
        sa.Column("load_date", sa.Date(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("source_location_id", sa.Integer(), nullable=False),
        sa.Column("destination_location_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
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
            "length(trim(load_number)) > 0",
            name="ck_route_loads_number_not_blank",
        ),
        sa.CheckConstraint(
            "source_location_id <> destination_location_id",
            name="ck_route_loads_locations_different",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_route_loads_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_route_loads_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["destination_location_id"], ["inventory_locations.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["delivery_routes.id"]),
        sa.ForeignKeyConstraint(["source_location_id"], ["inventory_locations.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("load_number"),
    )
    for index_name, column_name in (
        ("ix_route_loads_load_number", "load_number"),
        ("ix_route_loads_load_date", "load_date"),
        ("ix_route_loads_route_id", "route_id"),
        ("ix_route_loads_vehicle_id", "vehicle_id"),
        ("ix_route_loads_source_location_id", "source_location_id"),
        ("ix_route_loads_destination_location_id", "destination_location_id"),
        ("ix_route_loads_status", "status"),
    ):
        op.create_index(index_name, "route_loads", [column_name])

    op.create_table(
        "route_load_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_load_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_sku_snapshot", sa.String(length=80), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("product_presentation_snapshot", sa.String(length=255), nullable=True),
        sa.Column("quantity_loaded", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("source_exit_movement_id", sa.Integer(), nullable=False),
        sa.Column("destination_entry_movement_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity_loaded > 0",
            name="ck_route_load_items_quantity_positive",
        ),
        sa.CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_route_load_items_product_snapshot_not_blank",
        ),
        sa.ForeignKeyConstraint(
            ["destination_entry_movement_id"],
            ["inventory_movements.id"],
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["route_load_id"], ["route_loads.id"]),
        sa.ForeignKeyConstraint(
            ["source_exit_movement_id"],
            ["inventory_movements.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("destination_entry_movement_id"),
        sa.UniqueConstraint("source_exit_movement_id"),
        sa.UniqueConstraint(
            "route_load_id",
            "product_id",
            name="uq_route_load_items_product",
        ),
    )
    op.create_index(
        "ix_route_load_items_route_load_id",
        "route_load_items",
        ["route_load_id"],
    )
    op.create_index(
        "ix_route_load_items_product_id",
        "route_load_items",
        ["product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_route_load_items_product_id", table_name="route_load_items")
    op.drop_index("ix_route_load_items_route_load_id", table_name="route_load_items")
    op.drop_table("route_load_items")
    for index_name in (
        "ix_route_loads_status",
        "ix_route_loads_destination_location_id",
        "ix_route_loads_source_location_id",
        "ix_route_loads_vehicle_id",
        "ix_route_loads_route_id",
        "ix_route_loads_load_date",
        "ix_route_loads_load_number",
    ):
        op.drop_index(index_name, table_name="route_loads")
    op.drop_table("route_loads")
