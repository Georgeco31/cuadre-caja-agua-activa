"""create delivery routes

Revision ID: 0006_routes
Revises: 0005_employees
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0006_routes"
down_revision: str | None = "0005_employees"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "delivery_routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("zone", sa.String(length=120), nullable=True),
        sa.Column("sector", sa.String(length=120), nullable=True),
        sa.Column("service_days", sa.String(length=255), nullable=True),
        sa.Column("reference_driver", sa.String(length=255), nullable=True),
        sa.Column("reference_vehicle", sa.String(length=255), nullable=True),
        sa.Column(
            "expected_daily_cash",
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
            name="ck_delivery_routes_name_not_blank",
        ),
        sa.CheckConstraint(
            "expected_daily_cash >= 0",
            name="ck_delivery_routes_expected_cash_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )


def downgrade() -> None:
    op.drop_table("delivery_routes")
