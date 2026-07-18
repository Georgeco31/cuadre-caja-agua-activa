"""add credit fields to sales

Revision ID: 0009_credit_sales
Revises: 0008_cash_sales
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0009_credit_sales"
down_revision: str | None = "0008_cash_sales"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column(
            "paid_amount",
            sa.Numeric(precision=14, scale=2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
    )
    op.add_column(
        "sales",
        sa.Column(
            "balance_amount",
            sa.Numeric(precision=14, scale=2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
    )
    op.add_column(
        "sales",
        sa.Column(
            "credit_status",
            sa.String(length=20),
            server_default=sa.text("'none'"),
            nullable=False,
        ),
    )
    op.add_column("sales", sa.Column("due_date", sa.Date(), nullable=True))

    op.execute(
        "UPDATE sales SET paid_amount = total_amount, balance_amount = 0.00, "
        "credit_status = 'none' WHERE sale_type = 'cash'"
    )

    op.drop_constraint("ck_sales_sale_type", "sales", type_="check")
    op.create_check_constraint(
        "ck_sales_sale_type",
        "sales",
        "sale_type IN ('cash', 'credit')",
    )
    op.create_check_constraint(
        "ck_sales_paid_amount_nonnegative",
        "sales",
        "paid_amount >= 0",
    )
    op.create_check_constraint(
        "ck_sales_balance_amount_nonnegative",
        "sales",
        "balance_amount >= 0",
    )
    op.create_check_constraint(
        "ck_sales_credit_status",
        "sales",
        "credit_status IN ('none', 'pending', 'paid', 'voided')",
    )
    op.create_check_constraint(
        "ck_sales_credit_customer_required",
        "sales",
        "sale_type != 'credit' OR customer_id IS NOT NULL",
    )
    op.create_check_constraint(
        "ck_sales_amounts_by_type",
        "sales",
        "(sale_type = 'cash' AND paid_amount = total_amount "
        "AND balance_amount = 0 AND credit_status = 'none') OR "
        "(sale_type = 'credit')",
    )
    op.create_index(
        "ix_sales_customer_credit_balance",
        "sales",
        ["customer_id", "sale_type", "status", "balance_amount"],
    )


def downgrade() -> None:
    op.drop_index("ix_sales_customer_credit_balance", table_name="sales")
    op.drop_constraint("ck_sales_amounts_by_type", "sales", type_="check")
    op.drop_constraint(
        "ck_sales_credit_customer_required",
        "sales",
        type_="check",
    )
    op.drop_constraint("ck_sales_credit_status", "sales", type_="check")
    op.drop_constraint(
        "ck_sales_balance_amount_nonnegative",
        "sales",
        type_="check",
    )
    op.drop_constraint(
        "ck_sales_paid_amount_nonnegative",
        "sales",
        type_="check",
    )
    op.execute("UPDATE sales SET sale_type = 'cash' WHERE sale_type = 'credit'")
    op.drop_constraint("ck_sales_sale_type", "sales", type_="check")
    op.create_check_constraint(
        "ck_sales_sale_type",
        "sales",
        "sale_type = 'cash'",
    )
    op.drop_column("sales", "due_date")
    op.drop_column("sales", "credit_status")
    op.drop_column("sales", "balance_amount")
    op.drop_column("sales", "paid_amount")
