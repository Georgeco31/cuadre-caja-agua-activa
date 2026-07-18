"""create products

Revision ID: 0004_products
Revises: 0003_customers
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0004_products"
down_revision: str | None = "0003_customers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category",
            sa.String(length=20),
            server_default=sa.text("'other'"),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=20),
            server_default=sa.text("'unit'"),
            nullable=False,
        ),
        sa.Column("presentation", sa.String(length=100), nullable=True),
        sa.Column("default_price", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "cost_estimate",
            sa.Numeric(12, 2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "is_returnable_container",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_products_name_not_blank",
        ),
        sa.CheckConstraint(
            "category IN ('water', 'bottle', 'gallon', 'dispenser', 'container', 'other')",
            name="ck_products_category",
        ),
        sa.CheckConstraint(
            "unit IN ('unit', 'pack', 'liter', 'gallon', 'bottle', 'container', 'other')",
            name="ck_products_unit",
        ),
        sa.CheckConstraint(
            "default_price >= 0",
            name="ck_products_default_price_nonnegative",
        ),
        sa.CheckConstraint(
            "cost_estimate >= 0",
            name="ck_products_cost_estimate_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
    )


def downgrade() -> None:
    op.drop_table("products")
