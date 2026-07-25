"""create operating expenses

Revision ID: 0021_op_expenses
Revises: 0020_price_lists
Create Date: 2026-07-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0021_op_expenses"
down_revision: str | None = "0020_price_lists"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "operating_expense_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
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
            "length(trim(name)) > 0",
            name="ck_operating_expense_categories_name_not_blank",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        "ix_operating_expense_categories_name",
        "operating_expense_categories",
        ["name"],
    )
    op.create_index(
        "ix_operating_expense_categories_is_active",
        "operating_expense_categories",
        ["is_active"],
    )

    op.create_table(
        "recurring_operating_expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column("frequency", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column(
            "payment_method",
            sa.String(length=20),
            server_default=sa.text("'unknown'"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
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
            "length(trim(name)) > 0",
            name="ck_recurring_operating_expenses_name_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_recurring_operating_expenses_description_not_blank",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_recurring_operating_expenses_amount_positive",
        ),
        sa.CheckConstraint(
            "frequency IN ('weekly', 'monthly', 'quarterly', 'yearly')",
            name="ck_recurring_operating_expenses_frequency",
        ),
        sa.CheckConstraint(
            "payment_method IN "
            "('cash', 'transfer', 'card', 'check', 'other', 'unknown')",
            name="ck_recurring_operating_expenses_payment_method",
        ),
        sa.CheckConstraint(
            "end_date IS NULL OR start_date <= end_date",
            name="ck_recurring_operating_expenses_date_range",
        ),
        sa.CheckConstraint(
            "next_due_date IS NULL OR next_due_date >= start_date",
            name="ck_recurring_operating_expenses_next_due_after_start",
        ),
        sa.CheckConstraint(
            "next_due_date IS NULL OR end_date IS NULL "
            "OR next_due_date <= end_date",
            name="ck_recurring_operating_expenses_next_due_before_end",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["operating_expense_categories.id"],
        ),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for index_name, column_name in (
        ("ix_recurring_operating_expenses_name", "name"),
        ("ix_recurring_operating_expenses_category_id", "category_id"),
        ("ix_recurring_operating_expenses_supplier_id", "supplier_id"),
        ("ix_recurring_operating_expenses_frequency", "frequency"),
        ("ix_recurring_operating_expenses_start_date", "start_date"),
        ("ix_recurring_operating_expenses_next_due_date", "next_due_date"),
        ("ix_recurring_operating_expenses_payment_method", "payment_method"),
        ("ix_recurring_operating_expenses_is_active", "is_active"),
    ):
        op.create_index(
            index_name,
            "recurring_operating_expenses",
            [column_name],
        )

    op.create_table(
        "operating_expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("expense_number", sa.String(length=80), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "payment_status",
            sa.String(length=20),
            server_default=sa.text("'unpaid'"),
            nullable=False,
        ),
        sa.Column(
            "payment_method",
            sa.String(length=20),
            server_default=sa.text("'unknown'"),
            nullable=False,
        ),
        sa.Column("document_number", sa.String(length=120), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column("recurring_template_id", sa.Integer(), nullable=True),
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
            "length(trim(expense_number)) > 0",
            name="ck_operating_expenses_number_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_operating_expenses_description_not_blank",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_operating_expenses_amount_positive",
        ),
        sa.CheckConstraint(
            "payment_status IN ('unpaid', 'paid', 'partial')",
            name="ck_operating_expenses_payment_status",
        ),
        sa.CheckConstraint(
            "payment_method IN "
            "('cash', 'transfer', 'card', 'check', 'other', 'unknown')",
            name="ck_operating_expenses_payment_method",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_operating_expenses_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_operating_expenses_void_state",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["operating_expense_categories.id"],
        ),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(
            ["recurring_template_id"],
            ["recurring_operating_expenses.id"],
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("expense_number"),
    )
    for index_name, column_name in (
        ("ix_operating_expenses_expense_number", "expense_number"),
        ("ix_operating_expenses_expense_date", "expense_date"),
        ("ix_operating_expenses_category_id", "category_id"),
        ("ix_operating_expenses_supplier_id", "supplier_id"),
        ("ix_operating_expenses_payment_status", "payment_status"),
        ("ix_operating_expenses_payment_method", "payment_method"),
        ("ix_operating_expenses_document_number", "document_number"),
        ("ix_operating_expenses_due_date", "due_date"),
        ("ix_operating_expenses_paid_date", "paid_date"),
        ("ix_operating_expenses_recurring_template_id", "recurring_template_id"),
        ("ix_operating_expenses_status", "status"),
    ):
        op.create_index(index_name, "operating_expenses", [column_name])


def downgrade() -> None:
    for index_name in (
        "ix_operating_expenses_status",
        "ix_operating_expenses_recurring_template_id",
        "ix_operating_expenses_paid_date",
        "ix_operating_expenses_due_date",
        "ix_operating_expenses_document_number",
        "ix_operating_expenses_payment_method",
        "ix_operating_expenses_payment_status",
        "ix_operating_expenses_supplier_id",
        "ix_operating_expenses_category_id",
        "ix_operating_expenses_expense_date",
        "ix_operating_expenses_expense_number",
    ):
        op.drop_index(index_name, table_name="operating_expenses")
    op.drop_table("operating_expenses")

    for index_name in (
        "ix_recurring_operating_expenses_is_active",
        "ix_recurring_operating_expenses_payment_method",
        "ix_recurring_operating_expenses_next_due_date",
        "ix_recurring_operating_expenses_start_date",
        "ix_recurring_operating_expenses_frequency",
        "ix_recurring_operating_expenses_supplier_id",
        "ix_recurring_operating_expenses_category_id",
        "ix_recurring_operating_expenses_name",
    ):
        op.drop_index(index_name, table_name="recurring_operating_expenses")
    op.drop_table("recurring_operating_expenses")

    op.drop_index(
        "ix_operating_expense_categories_is_active",
        table_name="operating_expense_categories",
    )
    op.drop_index(
        "ix_operating_expense_categories_name",
        table_name="operating_expense_categories",
    )
    op.drop_table("operating_expense_categories")
