"""create route returns

Revision ID: 0015_route_returns
Revises: 0014_route_loads
Create Date: 2026-07-19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0015_route_returns"
down_revision: str | None = "0014_route_loads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "route_returns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("return_number", sa.String(length=80), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=False),
        sa.Column("route_load_id", sa.Integer(), nullable=False),
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
            "length(trim(return_number)) > 0",
            name="ck_route_returns_number_not_blank",
        ),
        sa.CheckConstraint(
            "source_location_id <> destination_location_id",
            name="ck_route_returns_locations_different",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_route_returns_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_route_returns_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["destination_location_id"], ["inventory_locations.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["delivery_routes.id"]),
        sa.ForeignKeyConstraint(["route_load_id"], ["route_loads.id"]),
        sa.ForeignKeyConstraint(["source_location_id"], ["inventory_locations.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("return_number"),
    )
    for index_name, column_name in (
        ("ix_route_returns_return_number", "return_number"),
        ("ix_route_returns_return_date", "return_date"),
        ("ix_route_returns_route_load_id", "route_load_id"),
        ("ix_route_returns_route_id", "route_id"),
        ("ix_route_returns_vehicle_id", "vehicle_id"),
        ("ix_route_returns_source_location_id", "source_location_id"),
        ("ix_route_returns_destination_location_id", "destination_location_id"),
        ("ix_route_returns_status", "status"),
    ):
        op.create_index(index_name, "route_returns", [column_name])
    op.create_index(
        "uq_route_returns_active_route_load",
        "route_returns",
        ["route_load_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "route_return_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_return_id", sa.Integer(), nullable=False),
        sa.Column("route_load_item_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_sku_snapshot", sa.String(length=80), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("product_presentation_snapshot", sa.String(length=255), nullable=True),
        sa.Column("quantity_returned", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("source_exit_movement_id", sa.Integer(), nullable=False),
        sa.Column("destination_entry_movement_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity_returned > 0",
            name="ck_route_return_items_quantity_positive",
        ),
        sa.CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_route_return_items_product_snapshot_not_blank",
        ),
        sa.ForeignKeyConstraint(
            ["destination_entry_movement_id"],
            ["inventory_movements.id"],
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["route_load_item_id"], ["route_load_items.id"]),
        sa.ForeignKeyConstraint(["route_return_id"], ["route_returns.id"]),
        sa.ForeignKeyConstraint(
            ["source_exit_movement_id"],
            ["inventory_movements.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("destination_entry_movement_id"),
        sa.UniqueConstraint("source_exit_movement_id"),
        sa.UniqueConstraint(
            "route_return_id",
            "route_load_item_id",
            name="uq_route_return_items_load_item",
        ),
    )
    for index_name, column_name in (
        ("ix_route_return_items_route_return_id", "route_return_id"),
        ("ix_route_return_items_route_load_item_id", "route_load_item_id"),
        ("ix_route_return_items_product_id", "product_id"),
    ):
        op.create_index(index_name, "route_return_items", [column_name])


def downgrade() -> None:
    for index_name in (
        "ix_route_return_items_product_id",
        "ix_route_return_items_route_load_item_id",
        "ix_route_return_items_route_return_id",
    ):
        op.drop_index(index_name, table_name="route_return_items")
    op.drop_table("route_return_items")
    for index_name in (
        "uq_route_returns_active_route_load",
        "ix_route_returns_status",
        "ix_route_returns_destination_location_id",
        "ix_route_returns_source_location_id",
        "ix_route_returns_vehicle_id",
        "ix_route_returns_route_id",
        "ix_route_returns_route_load_id",
        "ix_route_returns_return_date",
        "ix_route_returns_return_number",
    ):
        op.drop_index(index_name, table_name="route_returns")
    op.drop_table("route_returns")
