"""create route cash receipts

Revision ID: 0018_route_receipts
Revises: 0017_route_closures
Create Date: 2026-07-23
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0018_route_receipts"
down_revision: str | None = "0017_route_closures"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "route_cash_receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receipt_number", sa.String(length=80), nullable=False),
        sa.Column("receipt_date", sa.Date(), nullable=False),
        sa.Column("route_closure_id", sa.Integer(), nullable=False),
        sa.Column("cash_session_id", sa.Integer(), nullable=False),
        sa.Column("route_load_id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column(
            "closure_number_snapshot",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column("route_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("vehicle_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column(
            "delivered_cash_total",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "received_amount",
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
            "length(trim(receipt_number)) > 0",
            name="ck_route_cash_receipts_number_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(closure_number_snapshot)) > 0",
            name="ck_route_cash_receipts_closure_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(route_name_snapshot)) > 0",
            name="ck_route_cash_receipts_route_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(vehicle_name_snapshot)) > 0",
            name="ck_route_cash_receipts_vehicle_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "delivered_cash_total >= 0 AND received_amount >= 0",
            name="ck_route_cash_receipts_amounts_nonnegative",
        ),
        sa.CheckConstraint(
            "difference_amount = received_amount - delivered_cash_total",
            name="ck_route_cash_receipts_difference",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_route_cash_receipts_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_route_cash_receipts_void_state",
        ),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["route_closure_id"], ["route_closures.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["delivery_routes.id"]),
        sa.ForeignKeyConstraint(["route_load_id"], ["route_loads.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("receipt_number"),
    )
    for index_name, column_name in (
        ("ix_route_cash_receipts_receipt_number", "receipt_number"),
        ("ix_route_cash_receipts_receipt_date", "receipt_date"),
        ("ix_route_cash_receipts_route_closure_id", "route_closure_id"),
        ("ix_route_cash_receipts_cash_session_id", "cash_session_id"),
        ("ix_route_cash_receipts_route_load_id", "route_load_id"),
        ("ix_route_cash_receipts_route_id", "route_id"),
        ("ix_route_cash_receipts_vehicle_id", "vehicle_id"),
        ("ix_route_cash_receipts_status", "status"),
    ):
        op.create_index(index_name, "route_cash_receipts", [column_name])
    op.create_index(
        "uq_route_cash_receipts_active_closure",
        "route_cash_receipts",
        ["route_closure_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    for index_name in (
        "uq_route_cash_receipts_active_closure",
        "ix_route_cash_receipts_status",
        "ix_route_cash_receipts_vehicle_id",
        "ix_route_cash_receipts_route_id",
        "ix_route_cash_receipts_route_load_id",
        "ix_route_cash_receipts_cash_session_id",
        "ix_route_cash_receipts_route_closure_id",
        "ix_route_cash_receipts_receipt_date",
        "ix_route_cash_receipts_receipt_number",
    ):
        op.drop_index(index_name, table_name="route_cash_receipts")
    op.drop_table("route_cash_receipts")
