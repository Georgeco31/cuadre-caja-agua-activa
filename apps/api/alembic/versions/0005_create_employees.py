"""create employees

Revision ID: 0005_employees
Revises: 0004_products
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0005_employees"
down_revision: str | None = "0004_products"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("identification", sa.String(length=50), nullable=True),
        sa.Column("primary_phone", sa.String(length=50), nullable=True),
        sa.Column("secondary_phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("job_position", sa.String(length=120), nullable=True),
        sa.Column(
            "employee_type",
            sa.String(length=20),
            server_default=sa.text("'other'"),
            nullable=False,
        ),
        sa.Column(
            "base_salary",
            sa.Numeric(12, 2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "payment_frequency",
            sa.String(length=20),
            server_default=sa.text("'monthly'"),
            nullable=False,
        ),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("termination_date", sa.Date(), nullable=True),
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
            "length(trim(first_name)) > 0",
            name="ck_employees_first_name_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(last_name)) > 0",
            name="ck_employees_last_name_not_blank",
        ),
        sa.CheckConstraint(
            "employee_type IN ('driver', 'assistant', 'office', 'production', 'sales', 'other')",
            name="ck_employees_employee_type",
        ),
        sa.CheckConstraint(
            "payment_frequency IN ('daily', 'weekly', 'biweekly', 'monthly', 'other')",
            name="ck_employees_payment_frequency",
        ),
        sa.CheckConstraint(
            "base_salary >= 0",
            name="ck_employees_base_salary_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identification"),
    )


def downgrade() -> None:
    op.drop_table("employees")
