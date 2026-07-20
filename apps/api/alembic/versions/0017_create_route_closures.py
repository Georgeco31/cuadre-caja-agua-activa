"""create route closures

Revision ID: 0017_route_closures
Revises: 0016_route_links
Create Date: 2026-07-19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0017_route_closures"
down_revision: str | None = "0016_route_links"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "route_closures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("closure_number", sa.String(length=80), nullable=False),
        sa.Column("closure_date", sa.Date(), nullable=False),
        sa.Column("route_load_id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("load_number_snapshot", sa.String(length=80), nullable=False),
        sa.Column("route_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("vehicle_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column(
            "cash_sales_total",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "credit_sales_total",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "payments_total",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "expected_cash_total",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "delivered_cash_total",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "difference_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
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
            "length(trim(closure_number)) > 0",
            name="ck_route_closures_number_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(load_number_snapshot)) > 0",
            name="ck_route_closures_load_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(route_name_snapshot)) > 0",
            name="ck_route_closures_route_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(vehicle_name_snapshot)) > 0",
            name="ck_route_closures_vehicle_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "cash_sales_total >= 0 AND credit_sales_total >= 0 "
            "AND payments_total >= 0 AND expected_cash_total >= 0 "
            "AND delivered_cash_total >= 0",
            name="ck_route_closures_amounts_nonnegative",
        ),
        sa.CheckConstraint(
            "expected_cash_total = cash_sales_total + payments_total",
            name="ck_route_closures_expected_cash",
        ),
        sa.CheckConstraint(
            "difference_amount = delivered_cash_total - expected_cash_total",
            name="ck_route_closures_difference",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_route_closures_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_route_closures_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["delivery_routes.id"]),
        sa.ForeignKeyConstraint(["route_load_id"], ["route_loads.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("closure_number"),
    )
    for index_name, column_name in (
        ("ix_route_closures_closure_number", "closure_number"),
        ("ix_route_closures_closure_date", "closure_date"),
        ("ix_route_closures_route_load_id", "route_load_id"),
        ("ix_route_closures_route_id", "route_id"),
        ("ix_route_closures_vehicle_id", "vehicle_id"),
        ("ix_route_closures_status", "status"),
    ):
        op.create_index(index_name, "route_closures", [column_name])
    op.create_index(
        "uq_route_closures_active_route_load",
        "route_closures",
        ["route_load_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    for index_name in (
        "uq_route_closures_active_route_load",
        "ix_route_closures_status",
        "ix_route_closures_vehicle_id",
        "ix_route_closures_route_id",
        "ix_route_closures_route_load_id",
        "ix_route_closures_closure_date",
        "ix_route_closures_closure_number",
    ):
        op.drop_index(index_name, table_name="route_closures")
    op.drop_table("route_closures")
