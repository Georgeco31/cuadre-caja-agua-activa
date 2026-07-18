"""create vehicles

Revision ID: 0007_vehicles
Revises: 0006_routes
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0007_vehicles"
down_revision: str | None = "0006_routes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("plate", sa.String(length=50), nullable=True),
        sa.Column(
            "vehicle_type",
            sa.String(length=20),
            server_default=sa.text("'other'"),
            nullable=False,
        ),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("color", sa.String(length=80), nullable=True),
        sa.Column(
            "fuel_type",
            sa.String(length=20),
            server_default=sa.text("'other'"),
            nullable=False,
        ),
        sa.Column("capacity_reference", sa.String(length=255), nullable=True),
        sa.Column("reference_driver", sa.String(length=255), nullable=True),
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
            name="ck_vehicles_name_not_blank",
        ),
        sa.CheckConstraint(
            "vehicle_type IN ('truck', 'van', 'motorcycle', 'car', 'other')",
            name="ck_vehicles_vehicle_type",
        ),
        sa.CheckConstraint(
            "fuel_type IN ('gasoline', 'diesel', 'electric', 'hybrid', 'other')",
            name="ck_vehicles_fuel_type",
        ),
        sa.CheckConstraint(
            "year IS NULL OR (year >= 1900 AND year <= 2100)",
            name="ck_vehicles_year_reasonable",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("plate"),
    )


def downgrade() -> None:
    op.drop_table("vehicles")
