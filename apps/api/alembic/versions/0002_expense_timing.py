"""add expense timing to expenses

Revision ID: 0002_expense_timing
Revises: 0001_create_initial_tables
Create Date: 2026-07-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_expense_timing"
down_revision: str | None = "0001_create_initial_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "expenses",
        sa.Column(
            "expense_timing",
            sa.String(length=20),
            server_default=sa.text("'after_count'"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_expenses_expense_timing",
        "expenses",
        "expense_timing IN ('before_count', 'after_count')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_expenses_expense_timing",
        "expenses",
        type_="check",
    )
    op.drop_column("expenses", "expense_timing")
