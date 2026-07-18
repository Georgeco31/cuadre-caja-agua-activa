"""create customers

Revision ID: 0003_customers
Revises: 0002_expense_timing
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0003_customers"
down_revision: str | None = "0002_expense_timing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("primary_phone", sa.String(length=50), nullable=True),
        sa.Column("secondary_phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("sector", sa.String(length=120), nullable=True),
        sa.Column(
            "customer_type",
            sa.String(length=20),
            server_default=sa.text("'household'"),
            nullable=False,
        ),
        sa.Column("route_reference", sa.String(length=150), nullable=True),
        sa.Column(
            "credit_allowed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "credit_limit",
            sa.Numeric(12, 2),
            server_default=sa.text("0.00"),
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
            name="ck_customers_name_not_blank",
        ),
        sa.CheckConstraint(
            "customer_type IN ('household', 'store', 'business', 'distributor', 'other')",
            name="ck_customers_customer_type",
        ),
        sa.CheckConstraint(
            "credit_limit >= 0",
            name="ck_customers_credit_limit_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("primary_phone"),
    )


def downgrade() -> None:
    op.drop_table("customers")
