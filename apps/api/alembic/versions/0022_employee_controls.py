"""create employee attendance, advances and loans

Revision ID: 0022_employee_controls
Revises: 0021_op_expenses
Create Date: 2026-07-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0022_employee_controls"
down_revision: str | None = "0021_op_expenses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employee_attendance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("check_in_time", sa.Time(), nullable=True),
        sa.Column("check_out_time", sa.Time(), nullable=True),
        sa.Column(
            "hours_worked",
            sa.Numeric(precision=8, scale=2),
            nullable=True,
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
            "status IN "
            "('present', 'absent', 'late', 'permission', 'vacation', 'sick')",
            name="ck_employee_attendance_status",
        ),
        sa.CheckConstraint(
            "hours_worked IS NULL OR hours_worked >= 0",
            name="ck_employee_attendance_hours_nonnegative",
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "employee_id",
            "attendance_date",
            name="uq_employee_attendance_employee_date",
        ),
    )
    for index_name, column_name in (
        ("ix_employee_attendance_employee_id", "employee_id"),
        ("ix_employee_attendance_attendance_date", "attendance_date"),
        ("ix_employee_attendance_status", "status"),
    ):
        op.create_index(index_name, "employee_attendance", [column_name])

    op.create_table(
        "employee_advances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("advance_number", sa.String(length=80), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("advance_date", sa.Date(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=False),
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
            "length(trim(advance_number)) > 0",
            name="ck_employee_advances_number_not_blank",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_employee_advances_amount_positive",
        ),
        sa.CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_employee_advances_reason_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_employee_advances_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_employee_advances_void_state",
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("advance_number"),
    )
    for index_name, column_name in (
        ("ix_employee_advances_advance_number", "advance_number"),
        ("ix_employee_advances_employee_id", "employee_id"),
        ("ix_employee_advances_advance_date", "advance_date"),
        ("ix_employee_advances_status", "status"),
    ):
        op.create_index(index_name, "employee_advances", [column_name])

    op.create_table(
        "employee_loans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("loan_number", sa.String(length=80), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("loan_date", sa.Date(), nullable=False),
        sa.Column(
            "principal_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "paid_amount",
            sa.Numeric(precision=14, scale=2),
            server_default=sa.text("'0.00'"),
            nullable=False,
        ),
        sa.Column(
            "balance_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=False),
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
            "length(trim(loan_number)) > 0",
            name="ck_employee_loans_number_not_blank",
        ),
        sa.CheckConstraint(
            "principal_amount > 0",
            name="ck_employee_loans_principal_positive",
        ),
        sa.CheckConstraint(
            "paid_amount >= 0 AND paid_amount <= principal_amount",
            name="ck_employee_loans_paid_valid",
        ),
        sa.CheckConstraint(
            "balance_amount >= 0 AND "
            "balance_amount = principal_amount - paid_amount",
            name="ck_employee_loans_balance_valid",
        ),
        sa.CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_employee_loans_reason_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'paid', 'voided')",
            name="ck_employee_loans_status",
        ),
        sa.CheckConstraint(
            "(status = 'paid' AND balance_amount = 0) OR "
            "(status = 'active' AND balance_amount > 0) OR "
            "status = 'voided'",
            name="ck_employee_loans_status_balance",
        ),
        sa.CheckConstraint(
            "(status IN ('active', 'paid') AND void_reason IS NULL "
            "AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_employee_loans_void_state",
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("loan_number"),
    )
    for index_name, column_name in (
        ("ix_employee_loans_loan_number", "loan_number"),
        ("ix_employee_loans_employee_id", "employee_id"),
        ("ix_employee_loans_loan_date", "loan_date"),
        ("ix_employee_loans_status", "status"),
    ):
        op.create_index(index_name, "employee_loans", [column_name])

    op.create_table(
        "employee_loan_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_number", sa.String(length=80), nullable=False),
        sa.Column("employee_loan_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
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
            "length(trim(payment_number)) > 0",
            name="ck_employee_loan_payments_number_not_blank",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_employee_loan_payments_amount_positive",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_employee_loan_payments_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_employee_loan_payments_void_state",
        ),
        sa.ForeignKeyConstraint(
            ["employee_loan_id"],
            ["employee_loans.id"],
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_number"),
    )
    for index_name, column_name in (
        ("ix_employee_loan_payments_payment_number", "payment_number"),
        ("ix_employee_loan_payments_employee_loan_id", "employee_loan_id"),
        ("ix_employee_loan_payments_employee_id", "employee_id"),
        ("ix_employee_loan_payments_payment_date", "payment_date"),
        ("ix_employee_loan_payments_status", "status"),
    ):
        op.create_index(index_name, "employee_loan_payments", [column_name])


def downgrade() -> None:
    for index_name in (
        "ix_employee_loan_payments_status",
        "ix_employee_loan_payments_payment_date",
        "ix_employee_loan_payments_employee_id",
        "ix_employee_loan_payments_employee_loan_id",
        "ix_employee_loan_payments_payment_number",
    ):
        op.drop_index(index_name, table_name="employee_loan_payments")
    op.drop_table("employee_loan_payments")

    for index_name in (
        "ix_employee_loans_status",
        "ix_employee_loans_loan_date",
        "ix_employee_loans_employee_id",
        "ix_employee_loans_loan_number",
    ):
        op.drop_index(index_name, table_name="employee_loans")
    op.drop_table("employee_loans")

    for index_name in (
        "ix_employee_advances_status",
        "ix_employee_advances_advance_date",
        "ix_employee_advances_employee_id",
        "ix_employee_advances_advance_number",
    ):
        op.drop_index(index_name, table_name="employee_advances")
    op.drop_table("employee_advances")

    for index_name in (
        "ix_employee_attendance_status",
        "ix_employee_attendance_attendance_date",
        "ix_employee_attendance_employee_id",
    ):
        op.drop_index(index_name, table_name="employee_attendance")
    op.drop_table("employee_attendance")
