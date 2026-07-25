"""create base payroll runs

Revision ID: 0023_payroll
Revises: 0022_employee_controls
Create Date: 2026-07-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0023_payroll"
down_revision: str | None = "0022_employee_controls"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payroll_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_number", sa.String(length=80), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("payroll_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column("employees_count", sa.Integer(), nullable=False),
        sa.Column("gross_total", sa.Numeric(14, 2), nullable=False),
        sa.Column("bonuses_total", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "advances_deducted_total",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column(
            "loan_deductions_total",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column(
            "other_deductions_total",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column("total_deductions", sa.Numeric(14, 2), nullable=False),
        sa.Column("net_pay_total", sa.Numeric(14, 2), nullable=False),
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
            "length(trim(payroll_number)) > 0",
            name="ck_payroll_runs_number_not_blank",
        ),
        sa.CheckConstraint(
            "period_end >= period_start",
            name="ck_payroll_runs_period_valid",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_payroll_runs_status",
        ),
        sa.CheckConstraint(
            "employees_count > 0",
            name="ck_payroll_runs_employees_count_positive",
        ),
        sa.CheckConstraint(
            "gross_total >= 0 AND bonuses_total >= 0 "
            "AND advances_deducted_total >= 0 "
            "AND loan_deductions_total >= 0 "
            "AND other_deductions_total >= 0 "
            "AND total_deductions >= 0 AND net_pay_total >= 0",
            name="ck_payroll_runs_totals_nonnegative",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) "
            "OR (status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_payroll_runs_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payroll_number"),
    )
    for index_name, column_name in (
        ("ix_payroll_runs_payroll_number", "payroll_number"),
        ("ix_payroll_runs_period_start", "period_start"),
        ("ix_payroll_runs_period_end", "period_end"),
        ("ix_payroll_runs_payroll_date", "payroll_date"),
        ("ix_payroll_runs_status", "status"),
        ("ix_payroll_runs_created_by", "created_by"),
    ):
        op.create_index(index_name, "payroll_runs", [column_name])

    op.create_table(
        "payroll_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_run_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column(
            "employee_name_snapshot",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "employee_identification_snapshot",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "job_position_snapshot",
            sa.String(length=120),
            nullable=True,
        ),
        sa.Column(
            "payment_frequency_snapshot",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column("base_salary_snapshot", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "attendance_days",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "absent_days",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "permission_days",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "vacation_days",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "sick_days",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "late_days",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "hours_worked",
            sa.Numeric(10, 2),
            server_default=sa.text("'0.00'"),
            nullable=False,
        ),
        sa.Column("base_salary_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("bonus_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("other_income_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("gross_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "advances_deducted_amount",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column(
            "loan_deductions_amount",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column(
            "other_deductions_amount",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column(
            "total_deductions_amount",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column("net_pay_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
            "length(trim(employee_name_snapshot)) > 0",
            name="ck_payroll_items_employee_name_not_blank",
        ),
        sa.CheckConstraint(
            "base_salary_snapshot >= 0 AND base_salary_amount >= 0 "
            "AND bonus_amount >= 0 AND other_income_amount >= 0 "
            "AND gross_amount >= 0 AND advances_deducted_amount >= 0 "
            "AND loan_deductions_amount >= 0 "
            "AND other_deductions_amount >= 0 "
            "AND total_deductions_amount >= 0 AND net_pay_amount >= 0",
            name="ck_payroll_items_amounts_nonnegative",
        ),
        sa.CheckConstraint(
            "attendance_days >= 0 AND absent_days >= 0 "
            "AND permission_days >= 0 AND vacation_days >= 0 "
            "AND sick_days >= 0 AND late_days >= 0 AND hours_worked >= 0",
            name="ck_payroll_items_attendance_nonnegative",
        ),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "payroll_run_id",
            "employee_id",
            name="uq_payroll_items_run_employee",
        ),
    )
    for index_name, column_name in (
        ("ix_payroll_items_payroll_run_id", "payroll_run_id"),
        ("ix_payroll_items_employee_id", "employee_id"),
        ("ix_payroll_items_employee_name_snapshot", "employee_name_snapshot"),
    ):
        op.create_index(index_name, "payroll_items", [column_name])

    op.create_table(
        "payroll_item_advance_deductions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_item_id", sa.Integer(), nullable=False),
        sa.Column("employee_advance_id", sa.Integer(), nullable=False),
        sa.Column("amount_deducted", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "advance_number_snapshot",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column("advance_date_snapshot", sa.Date(), nullable=False),
        sa.Column("reason_snapshot", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount_deducted > 0",
            name="ck_payroll_item_advance_deductions_amount_positive",
        ),
        sa.ForeignKeyConstraint(
            ["payroll_item_id"],
            ["payroll_items.id"],
        ),
        sa.ForeignKeyConstraint(
            ["employee_advance_id"],
            ["employee_advances.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "payroll_item_id",
            "employee_advance_id",
            name="uq_payroll_item_advance_deductions_item_advance",
        ),
    )
    op.create_index(
        "ix_payroll_item_advance_deductions_payroll_item_id",
        "payroll_item_advance_deductions",
        ["payroll_item_id"],
    )
    op.create_index(
        "ix_payroll_item_advance_deductions_employee_advance_id",
        "payroll_item_advance_deductions",
        ["employee_advance_id"],
    )

    op.create_table(
        "payroll_item_loan_deductions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_item_id", sa.Integer(), nullable=False),
        sa.Column("employee_loan_id", sa.Integer(), nullable=False),
        sa.Column("amount_deducted", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "loan_number_snapshot",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column("loan_date_snapshot", sa.Date(), nullable=False),
        sa.Column(
            "loan_balance_snapshot",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column("reason_snapshot", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount_deducted > 0",
            name="ck_payroll_item_loan_deductions_amount_positive",
        ),
        sa.CheckConstraint(
            "loan_balance_snapshot >= amount_deducted",
            name="ck_payroll_item_loan_deductions_within_balance",
        ),
        sa.ForeignKeyConstraint(["payroll_item_id"], ["payroll_items.id"]),
        sa.ForeignKeyConstraint(["employee_loan_id"], ["employee_loans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "payroll_item_id",
            "employee_loan_id",
            name="uq_payroll_item_loan_deductions_item_loan",
        ),
    )
    op.create_index(
        "ix_payroll_item_loan_deductions_payroll_item_id",
        "payroll_item_loan_deductions",
        ["payroll_item_id"],
    )
    op.create_index(
        "ix_payroll_item_loan_deductions_employee_loan_id",
        "payroll_item_loan_deductions",
        ["employee_loan_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_payroll_item_loan_deductions_employee_loan_id",
        table_name="payroll_item_loan_deductions",
    )
    op.drop_index(
        "ix_payroll_item_loan_deductions_payroll_item_id",
        table_name="payroll_item_loan_deductions",
    )
    op.drop_table("payroll_item_loan_deductions")

    op.drop_index(
        "ix_payroll_item_advance_deductions_employee_advance_id",
        table_name="payroll_item_advance_deductions",
    )
    op.drop_index(
        "ix_payroll_item_advance_deductions_payroll_item_id",
        table_name="payroll_item_advance_deductions",
    )
    op.drop_table("payroll_item_advance_deductions")

    for index_name in (
        "ix_payroll_items_employee_name_snapshot",
        "ix_payroll_items_employee_id",
        "ix_payroll_items_payroll_run_id",
    ):
        op.drop_index(index_name, table_name="payroll_items")
    op.drop_table("payroll_items")

    for index_name in (
        "ix_payroll_runs_created_by",
        "ix_payroll_runs_status",
        "ix_payroll_runs_payroll_date",
        "ix_payroll_runs_period_end",
        "ix_payroll_runs_period_start",
        "ix_payroll_runs_payroll_number",
    ):
        op.drop_index(index_name, table_name="payroll_runs")
    op.drop_table("payroll_runs")
