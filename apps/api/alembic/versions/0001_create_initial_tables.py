"""create initial tables

Revision ID: 0001_create_initial_tables
Revises:
Create Date: 2026-06-29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_initial_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "denominations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("value", sa.Numeric(10, 2), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint("type IN ('coin', 'bill')", name="ck_denominations_type"),
        sa.CheckConstraint("value > 0", name="ck_denominations_value_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cash_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default=sa.text("'open'"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
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
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('open', 'closed', 'corrected')",
            name="ck_cash_sessions_status",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_date"),
    )
    op.create_table(
        "cash_count_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cash_session_id", sa.Integer(), nullable=False),
        sa.Column("denomination_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint(
            "quantity >= 0",
            name="ck_cash_count_items_quantity_nonnegative",
        ),
        sa.CheckConstraint(
            "subtotal >= 0",
            name="ck_cash_count_items_subtotal_nonnegative",
        ),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"]),
        sa.ForeignKeyConstraint(["denomination_id"], ["denominations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cash_session_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "correction_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cash_session_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("previous_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("new_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("correction_logs")
    op.drop_table("expenses")
    op.drop_table("cash_count_items")
    op.drop_table("cash_sessions")
    op.drop_table("denominations")
    op.drop_table("users")
