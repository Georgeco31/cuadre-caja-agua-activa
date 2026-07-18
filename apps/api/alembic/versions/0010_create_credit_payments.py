"""create credit payments

Revision ID: 0010_payments
Revises: 0009_credit_sales
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0010_payments"
down_revision: str | None = "0009_credit_sales"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "credit_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
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
            "amount > 0",
            name="ck_credit_payments_amount_positive",
        ),
        sa.CheckConstraint(
            "payment_method IN ('cash', 'transfer', 'card', 'other')",
            name="ck_credit_payments_payment_method",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_credit_payments_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_credit_payments_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_credit_payments_customer_id",
        "credit_payments",
        ["customer_id"],
    )
    op.create_index(
        "ix_credit_payments_payment_date",
        "credit_payments",
        ["payment_date"],
    )
    op.create_index(
        "ix_credit_payments_sale_id",
        "credit_payments",
        ["sale_id"],
    )
    op.create_index(
        "ix_credit_payments_status",
        "credit_payments",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_credit_payments_status", table_name="credit_payments")
    op.drop_index("ix_credit_payments_sale_id", table_name="credit_payments")
    op.drop_index(
        "ix_credit_payments_payment_date",
        table_name="credit_payments",
    )
    op.drop_index(
        "ix_credit_payments_customer_id",
        table_name="credit_payments",
    )
    op.drop_table("credit_payments")
