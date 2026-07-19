"""connect production to inventory

Revision ID: 0013_prod_inventory
Revises: 0012_production
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0013_prod_inventory"
down_revision: str | None = "0012_production"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_production_items_waste_not_greater_than_produced",
        "production_items",
        "quantity_waste <= quantity_produced",
    )
    op.create_table(
        "production_inventory_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("production_batch_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
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
            "status IN ('active', 'voided')",
            name="ck_production_inventory_applications_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_production_inventory_applications_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["inventory_locations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["production_batch_id"],
            ["production_batches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_production_inventory_applications_production_batch_id",
        "production_inventory_applications",
        ["production_batch_id"],
    )
    op.create_index(
        "ix_production_inventory_applications_location_id",
        "production_inventory_applications",
        ["location_id"],
    )
    op.create_index(
        "ix_production_inventory_applications_status",
        "production_inventory_applications",
        ["status"],
    )
    op.create_index(
        "uq_production_inventory_applications_active_batch",
        "production_inventory_applications",
        ["production_batch_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "production_inventory_application_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("production_item_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("inventory_movement_id", sa.Integer(), nullable=False),
        sa.Column(
            "quantity_applied",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity_applied > 0",
            name="ck_production_inventory_application_items_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["production_inventory_applications.id"],
        ),
        sa.ForeignKeyConstraint(
            ["inventory_movement_id"],
            ["inventory_movements.id"],
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(
            ["production_item_id"],
            ["production_items.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inventory_movement_id"),
        sa.UniqueConstraint(
            "application_id",
            "production_item_id",
            name="uq_production_inventory_application_items_source",
        ),
    )
    op.create_index(
        "ix_production_inventory_application_items_application_id",
        "production_inventory_application_items",
        ["application_id"],
    )
    op.create_index(
        "ix_production_inventory_application_items_product_id",
        "production_inventory_application_items",
        ["product_id"],
    )
    op.create_index(
        "ix_production_inventory_application_items_production_item_id",
        "production_inventory_application_items",
        ["production_item_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_production_inventory_application_items_production_item_id",
        table_name="production_inventory_application_items",
    )
    op.drop_index(
        "ix_production_inventory_application_items_product_id",
        table_name="production_inventory_application_items",
    )
    op.drop_index(
        "ix_production_inventory_application_items_application_id",
        table_name="production_inventory_application_items",
    )
    op.drop_table("production_inventory_application_items")
    op.drop_index(
        "uq_production_inventory_applications_active_batch",
        table_name="production_inventory_applications",
    )
    op.drop_index(
        "ix_production_inventory_applications_status",
        table_name="production_inventory_applications",
    )
    op.drop_index(
        "ix_production_inventory_applications_location_id",
        table_name="production_inventory_applications",
    )
    op.drop_index(
        "ix_production_inventory_applications_production_batch_id",
        table_name="production_inventory_applications",
    )
    op.drop_table("production_inventory_applications")
    op.drop_constraint(
        "ck_production_items_waste_not_greater_than_produced",
        "production_items",
        type_="check",
    )
