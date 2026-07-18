"""create base production

Revision ID: 0012_production
Revises: 0011_inventory
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0012_production"
down_revision: str | None = "0011_inventory"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "production_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("production_number", sa.String(length=50), nullable=False),
        sa.Column("production_date", sa.Date(), nullable=False),
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
            "length(trim(production_number)) > 0",
            name="ck_production_batches_number_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_production_batches_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_batches_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("production_number"),
    )
    op.create_index(
        "ix_production_batches_production_date",
        "production_batches",
        ["production_date"],
    )
    op.create_index(
        "ix_production_batches_status",
        "production_batches",
        ["status"],
    )

    op.create_table(
        "production_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("production_batch_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_sku_snapshot", sa.String(length=80), nullable=True),
        sa.Column(
            "product_name_snapshot",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "product_presentation_snapshot",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "quantity_produced",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column(
            "quantity_waste",
            sa.Numeric(precision=14, scale=3),
            server_default=sa.text("0.000"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_production_items_product_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "quantity_produced > 0",
            name="ck_production_items_quantity_produced_positive",
        ),
        sa.CheckConstraint(
            "quantity_waste >= 0",
            name="ck_production_items_quantity_waste_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["production_batch_id"],
            ["production_batches.id"],
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_production_items_production_batch_id",
        "production_items",
        ["production_batch_id"],
    )
    op.create_index(
        "ix_production_items_product_id",
        "production_items",
        ["product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_production_items_product_id", table_name="production_items")
    op.drop_index(
        "ix_production_items_production_batch_id",
        table_name="production_items",
    )
    op.drop_table("production_items")
    op.drop_index("ix_production_batches_status", table_name="production_batches")
    op.drop_index(
        "ix_production_batches_production_date",
        table_name="production_batches",
    )
    op.drop_table("production_batches")
