"""create independent simple route sheets

Revision ID: 0029_simple_routes
Revises: 0028_payroll_base
Create Date: 2026-08-05
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0029_simple_routes"
down_revision: str | None = "0028_payroll_base"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "simple_route_sheets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_date", sa.Date(), nullable=False),
        sa.Column("seller_name", sa.String(length=255), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("vehicle_id", sa.Integer(), nullable=True),
        sa.Column("route_label", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'draft'"),
            nullable=False,
        ),
        sa.Column("cash_delivered", sa.Numeric(14, 2), nullable=True),
        sa.Column(
            "cash_received_in_cash_session",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("cash_session_id", sa.Integer(), nullable=True),
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
        sa.Column("settled_by", sa.Integer(), nullable=True),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by", sa.Integer(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "length(trim(seller_name)) > 0",
            name="ck_simple_route_sheets_seller_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'in_progress', 'settled', 'cancelled')",
            name="ck_simple_route_sheets_status",
        ),
        sa.CheckConstraint(
            "cash_delivered IS NULL OR cash_delivered >= 0",
            name="ck_simple_route_sheets_cash_nonnegative",
        ),
        sa.CheckConstraint(
            "(cash_received_in_cash_session = false AND cash_session_id IS NULL) "
            "OR (cash_received_in_cash_session = true AND cash_session_id IS NOT NULL)",
            name="ck_simple_route_sheets_cash_receipt_state",
        ),
        sa.CheckConstraint(
            "status != 'settled' OR "
            "(cash_delivered IS NOT NULL AND settled_by IS NOT NULL "
            "AND settled_at IS NOT NULL)",
            name="ck_simple_route_sheets_settled_state",
        ),
        sa.CheckConstraint(
            "status != 'cancelled' OR "
            "(cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL "
            "AND length(trim(cancellation_reason)) > 0)",
            name="ck_simple_route_sheets_cancelled_state",
        ),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"]),
        sa.ForeignKeyConstraint(["cancelled_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["settled_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes(
        "simple_route_sheets",
        (
            "route_date",
            "seller_name",
            "employee_id",
            "vehicle_id",
            "route_label",
            "status",
            "cash_session_id",
        ),
    )

    op.create_table(
        "simple_route_trips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_sheet_id", sa.Integer(), nullable=False),
        sa.Column("trip_number", sa.Integer(), nullable=False),
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
            "trip_number > 0",
            name="ck_simple_route_trips_number_positive",
        ),
        sa.ForeignKeyConstraint(
            ["route_sheet_id"],
            ["simple_route_sheets.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "route_sheet_id",
            "trip_number",
            name="uq_simple_route_trips_sheet_number",
        ),
    )
    op.create_index(
        "ix_simple_route_trips_route_sheet_id",
        "simple_route_trips",
        ["route_sheet_id"],
    )

    op.create_table(
        "simple_route_trip_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("movement_type", sa.String(length=10), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("item_label", sa.String(length=255), nullable=False),
        sa.Column("item_category", sa.String(length=40), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "movement_type IN ('out', 'return')",
            name="ck_simple_route_trip_items_movement",
        ),
        sa.CheckConstraint(
            "length(trim(item_label)) > 0",
            name="ck_simple_route_trip_items_label_not_blank",
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_simple_route_trip_items_quantity_positive",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(
            ["trip_id"],
            ["simple_route_trips.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_simple_route_trip_items_trip_id",
        "simple_route_trip_items",
        ["trip_id"],
    )

    op.create_table(
        "simple_route_sales",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_sheet_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("customer_name_snapshot", sa.String(length=255), nullable=True),
        sa.Column("sale_type", sa.String(length=20), nullable=False),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("pending_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
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
            "sale_type IN ('cash', 'credit', 'partial')",
            name="ck_simple_route_sales_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_simple_route_sales_status",
        ),
        sa.CheckConstraint(
            "total_amount >= 0 AND paid_amount >= 0 AND pending_amount >= 0",
            name="ck_simple_route_sales_amounts_nonnegative",
        ),
        sa.CheckConstraint(
            "paid_amount + pending_amount = total_amount",
            name="ck_simple_route_sales_amounts_balance",
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(
            ["route_sheet_id"],
            ["simple_route_sheets.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("simple_route_sales", ("route_sheet_id", "sale_date"))

    op.create_table(
        "simple_route_sale_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("simple_route_sale_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("item_category", sa.String(length=40), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), nullable=False),
        sa.CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_simple_route_sale_items_name_not_blank",
        ),
        sa.CheckConstraint(
            "quantity > 0 AND unit_price >= 0 AND subtotal >= 0",
            name="ck_simple_route_sale_items_amounts",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(
            ["simple_route_sale_id"],
            ["simple_route_sales.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_simple_route_sale_items_simple_route_sale_id",
        "simple_route_sale_items",
        ["simple_route_sale_id"],
    )

    op.create_table(
        "simple_route_collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_sheet_id", sa.Integer(), nullable=False),
        sa.Column("simple_route_sale_id", sa.Integer(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("customer_name_snapshot", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("collection_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_simple_route_collections_amount_positive",
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(
            ["route_sheet_id"],
            ["simple_route_sheets.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["simple_route_sale_id"],
            ["simple_route_sales.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes(
        "simple_route_collections",
        ("route_sheet_id", "simple_route_sale_id", "collection_date"),
    )

    op.create_table(
        "simple_route_expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_sheet_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_simple_route_expenses_description_not_blank",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_simple_route_expenses_amount_positive",
        ),
        sa.ForeignKeyConstraint(
            ["route_sheet_id"],
            ["simple_route_sheets.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes("simple_route_expenses", ("route_sheet_id", "expense_date"))

    op.create_table(
        "simple_route_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_sheet_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["route_sheet_id"],
            ["simple_route_sheets.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_indexes(
        "simple_route_audit_logs",
        ("route_sheet_id", "created_at"),
    )

    op.create_table(
        "simple_route_cash_receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_sheet_id", sa.Integer(), nullable=False),
        sa.Column("cash_session_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("received_by", sa.Integer(), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount >= 0",
            name="ck_simple_route_cash_receipts_amount_nonnegative",
        ),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"]),
        sa.ForeignKeyConstraint(["received_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["route_sheet_id"], ["simple_route_sheets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "route_sheet_id",
            name="uq_simple_route_cash_receipts_sheet",
        ),
    )
    _create_indexes(
        "simple_route_cash_receipts",
        ("route_sheet_id", "cash_session_id"),
    )
    op.create_index(
        "ix_simple_route_cash_receipts_session_received",
        "simple_route_cash_receipts",
        ["cash_session_id", "received_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_simple_route_cash_receipts_session_received",
        table_name="simple_route_cash_receipts",
    )
    _drop_indexes(
        "simple_route_cash_receipts",
        ("route_sheet_id", "cash_session_id"),
    )
    op.drop_table("simple_route_cash_receipts")
    _drop_indexes("simple_route_audit_logs", ("route_sheet_id", "created_at"))
    op.drop_table("simple_route_audit_logs")
    _drop_indexes("simple_route_expenses", ("route_sheet_id", "expense_date"))
    op.drop_table("simple_route_expenses")
    _drop_indexes(
        "simple_route_collections",
        ("route_sheet_id", "simple_route_sale_id", "collection_date"),
    )
    op.drop_table("simple_route_collections")
    op.drop_index(
        "ix_simple_route_sale_items_simple_route_sale_id",
        table_name="simple_route_sale_items",
    )
    op.drop_table("simple_route_sale_items")
    _drop_indexes("simple_route_sales", ("route_sheet_id", "sale_date"))
    op.drop_table("simple_route_sales")
    op.drop_index(
        "ix_simple_route_trip_items_trip_id",
        table_name="simple_route_trip_items",
    )
    op.drop_table("simple_route_trip_items")
    op.drop_index(
        "ix_simple_route_trips_route_sheet_id",
        table_name="simple_route_trips",
    )
    op.drop_table("simple_route_trips")
    _drop_indexes(
        "simple_route_sheets",
        (
            "route_date",
            "seller_name",
            "employee_id",
            "vehicle_id",
            "route_label",
            "status",
            "cash_session_id",
        ),
    )
    op.drop_table("simple_route_sheets")


def _create_indexes(table_name: str, column_names: tuple[str, ...]) -> None:
    for column_name in column_names:
        op.create_index(
            f"ix_{table_name}_{column_name}",
            table_name,
            [column_name],
        )


def _drop_indexes(table_name: str, column_names: tuple[str, ...]) -> None:
    for column_name in reversed(column_names):
        op.drop_index(f"ix_{table_name}_{column_name}", table_name=table_name)
