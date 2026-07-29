"""complete the base payroll workflow and payment audit

Revision ID: 0028_payroll_base
Revises: 0027_sale_date_corrections
Create Date: 2026-07-29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0028_payroll_base"
down_revision: str | None = "0027_sale_date_corrections"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_payroll_runs_status",
        "payroll_runs",
        type_="check",
    )
    op.drop_constraint(
        "ck_payroll_runs_employees_count_positive",
        "payroll_runs",
        type_="check",
    )
    op.drop_constraint(
        "ck_payroll_runs_void_state",
        "payroll_runs",
        type_="check",
    )

    op.alter_column(
        "payroll_runs",
        "void_reason",
        new_column_name="cancellation_reason",
        existing_type=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "payroll_runs",
        "voided_at",
        new_column_name="cancelled_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    for column in (
        sa.Column("label", sa.String(length=160), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_by", sa.Integer(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by", sa.Integer(), nullable=True),
    ):
        op.add_column("payroll_runs", column)

    op.execute(
        sa.text(
            """
            UPDATE payroll_runs
            SET label = payroll_number,
                approved_by = CASE
                    WHEN status = 'active' THEN created_by
                    ELSE NULL
                END,
                approved_at = CASE
                    WHEN status = 'active' THEN created_at
                    ELSE NULL
                END,
                cancelled_by = CASE
                    WHEN status = 'voided' THEN created_by
                    ELSE NULL
                END,
                status = CASE
                    WHEN status = 'active' THEN 'approved'
                    ELSE 'cancelled'
                END
            """
        )
    )
    op.alter_column(
        "payroll_runs",
        "label",
        existing_type=sa.String(length=160),
        nullable=False,
    )
    op.alter_column(
        "payroll_runs",
        "status",
        existing_type=sa.String(length=20),
        existing_nullable=False,
        server_default=sa.text("'draft'"),
    )
    op.create_check_constraint(
        "ck_payroll_runs_label_not_blank",
        "payroll_runs",
        "length(trim(label)) > 0",
    )
    op.create_check_constraint(
        "ck_payroll_runs_status",
        "payroll_runs",
        "status IN ('draft', 'approved', 'paid', 'cancelled')",
    )
    op.create_check_constraint(
        "ck_payroll_runs_employees_count_nonnegative",
        "payroll_runs",
        "employees_count >= 0",
    )
    op.create_check_constraint(
        "ck_payroll_runs_workflow_state",
        "payroll_runs",
        """
        (
            status = 'draft'
            AND approved_by IS NULL AND approved_at IS NULL
            AND paid_by IS NULL AND paid_at IS NULL
            AND cancelled_by IS NULL AND cancelled_at IS NULL
            AND cancellation_reason IS NULL
        ) OR (
            status = 'approved'
            AND approved_by IS NOT NULL AND approved_at IS NOT NULL
            AND paid_by IS NULL AND paid_at IS NULL
            AND cancelled_by IS NULL AND cancelled_at IS NULL
            AND cancellation_reason IS NULL
        ) OR (
            status = 'paid'
            AND approved_by IS NOT NULL AND approved_at IS NOT NULL
            AND paid_by IS NOT NULL AND paid_at IS NOT NULL
            AND cancelled_by IS NULL AND cancelled_at IS NULL
            AND cancellation_reason IS NULL
        ) OR (
            status = 'cancelled'
            AND paid_by IS NULL AND paid_at IS NULL
            AND cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL
            AND length(trim(cancellation_reason)) > 0
            AND (
                (approved_by IS NULL AND approved_at IS NULL)
                OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)
            )
        )
        """,
    )
    for column_name in ("approved_by", "paid_by", "cancelled_by"):
        op.create_foreign_key(
            f"fk_payroll_runs_{column_name}_users",
            "payroll_runs",
            "users",
            [column_name],
            ["id"],
        )
        op.create_index(
            f"ix_payroll_runs_{column_name}",
            "payroll_runs",
            [column_name],
        )

    op.drop_constraint(
        "ck_employee_advances_status",
        "employee_advances",
        type_="check",
    )
    op.drop_constraint(
        "ck_employee_advances_void_state",
        "employee_advances",
        type_="check",
    )
    op.add_column(
        "employee_advances",
        sa.Column("deducted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "employee_advances",
        sa.Column("deducted_by", sa.Integer(), nullable=True),
    )
    op.add_column(
        "employee_advances",
        sa.Column("deducted_payroll_run_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_employee_advances_deducted_by_users",
        "employee_advances",
        "users",
        ["deducted_by"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_advances_deducted_payroll_run",
        "employee_advances",
        "payroll_runs",
        ["deducted_payroll_run_id"],
        ["id"],
    )
    op.create_index(
        "ix_employee_advances_deducted_payroll_run_id",
        "employee_advances",
        ["deducted_payroll_run_id"],
    )
    op.create_check_constraint(
        "ck_employee_advances_status",
        "employee_advances",
        "status IN ('active', 'deducted', 'voided')",
    )
    op.create_check_constraint(
        "ck_employee_advances_void_state",
        "employee_advances",
        """
        (
            status = 'active'
            AND void_reason IS NULL AND voided_at IS NULL
            AND deducted_at IS NULL AND deducted_by IS NULL
            AND deducted_payroll_run_id IS NULL
        ) OR (
            status = 'deducted'
            AND void_reason IS NULL AND voided_at IS NULL
            AND deducted_at IS NOT NULL AND deducted_by IS NOT NULL
            AND deducted_payroll_run_id IS NOT NULL
        ) OR (
            status = 'voided'
            AND length(trim(void_reason)) > 0 AND voided_at IS NOT NULL
            AND deducted_at IS NULL AND deducted_by IS NULL
            AND deducted_payroll_run_id IS NULL
        )
        """,
    )

    op.add_column(
        "employee_loan_payments",
        sa.Column("payroll_run_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_employee_loan_payments_payroll_run",
        "employee_loan_payments",
        "payroll_runs",
        ["payroll_run_id"],
        ["id"],
    )
    op.create_index(
        "ix_employee_loan_payments_payroll_run_id",
        "employee_loan_payments",
        ["payroll_run_id"],
    )

    op.add_column(
        "payroll_item_advance_deductions",
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "payroll_item_loan_deductions",
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "payroll_item_loan_deductions",
        sa.Column("loan_payment_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_payroll_item_loan_deductions_payment",
        "payroll_item_loan_deductions",
        "employee_loan_payments",
        ["loan_payment_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "uq_payroll_item_loan_deductions_payment",
        "payroll_item_loan_deductions",
        ["loan_payment_id"],
    )

    op.create_table(
        "payroll_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_run_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "action IN ('run_created', 'item_added', 'item_updated', "
            "'approved', 'paid', 'cancelled')",
            name="ck_payroll_audit_logs_action",
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_payroll_audit_logs_payroll_run_id",
        "payroll_audit_logs",
        ["payroll_run_id"],
    )
    op.create_index(
        "ix_payroll_audit_logs_actor_id",
        "payroll_audit_logs",
        ["actor_id"],
    )
    op.create_index(
        "ix_payroll_audit_logs_created_at",
        "payroll_audit_logs",
        ["created_at"],
    )
    op.execute(
        sa.text(
            """
            INSERT INTO payroll_audit_logs
                (payroll_run_id, action, actor_id, reason, details, created_at)
            SELECT
                id,
                'run_created',
                created_by,
                'Registro migrado desde el flujo base anterior',
                'migration=0028;legacy_status_migrated=true',
                created_at
            FROM payroll_runs
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    paid_runs = bind.scalar(
        sa.text("SELECT count(*) FROM payroll_runs WHERE status = 'paid'")
    )
    if paid_runs:
        raise RuntimeError(
            "No se puede revertir 0028: existen roles pagados con descuentos "
            "aplicados."
        )
    empty_runs = bind.scalar(
        sa.text("SELECT count(*) FROM payroll_runs WHERE employees_count = 0")
    )
    if empty_runs:
        raise RuntimeError(
            "No se puede revertir 0028: existen roles sin empleados que no "
            "son compatibles con el esquema anterior."
        )

    op.drop_index(
        "ix_payroll_audit_logs_created_at",
        table_name="payroll_audit_logs",
    )
    op.drop_index(
        "ix_payroll_audit_logs_actor_id",
        table_name="payroll_audit_logs",
    )
    op.drop_index(
        "ix_payroll_audit_logs_payroll_run_id",
        table_name="payroll_audit_logs",
    )
    op.drop_table("payroll_audit_logs")

    op.drop_constraint(
        "uq_payroll_item_loan_deductions_payment",
        "payroll_item_loan_deductions",
        type_="unique",
    )
    op.drop_constraint(
        "fk_payroll_item_loan_deductions_payment",
        "payroll_item_loan_deductions",
        type_="foreignkey",
    )
    op.drop_column("payroll_item_loan_deductions", "loan_payment_id")
    op.drop_column("payroll_item_loan_deductions", "applied_at")
    op.drop_column("payroll_item_advance_deductions", "applied_at")

    op.drop_index(
        "ix_employee_loan_payments_payroll_run_id",
        table_name="employee_loan_payments",
    )
    op.drop_constraint(
        "fk_employee_loan_payments_payroll_run",
        "employee_loan_payments",
        type_="foreignkey",
    )
    op.drop_column("employee_loan_payments", "payroll_run_id")

    op.drop_constraint(
        "ck_employee_advances_void_state",
        "employee_advances",
        type_="check",
    )
    op.drop_constraint(
        "ck_employee_advances_status",
        "employee_advances",
        type_="check",
    )
    op.drop_index(
        "ix_employee_advances_deducted_payroll_run_id",
        table_name="employee_advances",
    )
    op.drop_constraint(
        "fk_employee_advances_deducted_payroll_run",
        "employee_advances",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_employee_advances_deducted_by_users",
        "employee_advances",
        type_="foreignkey",
    )
    op.drop_column("employee_advances", "deducted_payroll_run_id")
    op.drop_column("employee_advances", "deducted_by")
    op.drop_column("employee_advances", "deducted_at")
    op.create_check_constraint(
        "ck_employee_advances_status",
        "employee_advances",
        "status IN ('active', 'voided')",
    )
    op.create_check_constraint(
        "ck_employee_advances_void_state",
        "employee_advances",
        "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) "
        "OR (status = 'voided' AND length(trim(void_reason)) > 0 "
        "AND voided_at IS NOT NULL)",
    )

    op.drop_constraint(
        "ck_payroll_runs_workflow_state",
        "payroll_runs",
        type_="check",
    )
    op.drop_constraint(
        "ck_payroll_runs_employees_count_nonnegative",
        "payroll_runs",
        type_="check",
    )
    op.drop_constraint(
        "ck_payroll_runs_status",
        "payroll_runs",
        type_="check",
    )
    op.drop_constraint(
        "ck_payroll_runs_label_not_blank",
        "payroll_runs",
        type_="check",
    )
    for column_name in ("cancelled_by", "paid_by", "approved_by"):
        op.drop_index(
            f"ix_payroll_runs_{column_name}",
            table_name="payroll_runs",
        )
        op.drop_constraint(
            f"fk_payroll_runs_{column_name}_users",
            "payroll_runs",
            type_="foreignkey",
        )

    op.execute(
        sa.text(
            """
            UPDATE payroll_runs
            SET status = CASE
                    WHEN status = 'cancelled' THEN 'voided'
                    ELSE 'active'
                END
            """
        )
    )
    op.alter_column(
        "payroll_runs",
        "status",
        existing_type=sa.String(length=20),
        existing_nullable=False,
        server_default=sa.text("'active'"),
    )
    op.drop_column("payroll_runs", "cancelled_by")
    op.drop_column("payroll_runs", "paid_at")
    op.drop_column("payroll_runs", "paid_by")
    op.drop_column("payroll_runs", "approved_at")
    op.drop_column("payroll_runs", "approved_by")
    op.drop_column("payroll_runs", "label")
    op.alter_column(
        "payroll_runs",
        "cancelled_at",
        new_column_name="voided_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "payroll_runs",
        "cancellation_reason",
        new_column_name="void_reason",
        existing_type=sa.Text(),
        existing_nullable=True,
    )
    op.create_check_constraint(
        "ck_payroll_runs_status",
        "payroll_runs",
        "status IN ('active', 'voided')",
    )
    op.create_check_constraint(
        "ck_payroll_runs_employees_count_positive",
        "payroll_runs",
        "employees_count > 0",
    )
    op.create_check_constraint(
        "ck_payroll_runs_void_state",
        "payroll_runs",
        "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) "
        "OR (status = 'voided' AND length(trim(void_reason)) > 0 "
        "AND voided_at IS NOT NULL)",
    )
