"""create cash sales

Revision ID: 0008_cash_sales
Revises: 0007_vehicles
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0008_cash_sales"
down_revision: str | None = "0007_vehicles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_number", sa.String(length=50), nullable=False),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("customer_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column(
            "sale_type",
            sa.String(length=20),
            server_default=sa.text("'cash'"),
            nullable=False,
        ),
        sa.Column(
            "payment_method",
            sa.String(length=20),
            server_default=sa.text("'cash'"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column("total_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("void_reason", sa.Text(), nullable=True),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
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
            "length(trim(sale_number)) > 0",
            name="ck_sales_sale_number_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(customer_name_snapshot)) > 0",
            name="ck_sales_customer_snapshot_not_blank",
        ),
        sa.CheckConstraint("sale_type = 'cash'", name="ck_sales_sale_type"),
        sa.CheckConstraint(
            "payment_method IN ('cash', 'transfer', 'card', 'other')",
            name="ck_sales_payment_method",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_sales_status",
        ),
        sa.CheckConstraint(
            "total_amount >= 0",
            name="ck_sales_total_amount_nonnegative",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sale_number"),
    )
    op.create_index("ix_sales_sale_date", "sales", ["sale_date"])
    op.create_index("ix_sales_customer_id", "sales", ["customer_id"])
    op.create_index("ix_sales_status", "sales", ["status"])

    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_sku_snapshot", sa.String(length=80), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column(
            "product_presentation_snapshot",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_sale_items_product_snapshot_not_blank",
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_sale_items_quantity_positive",
        ),
        sa.CheckConstraint(
            "unit_price >= 0",
            name="ck_sale_items_unit_price_nonnegative",
        ),
        sa.CheckConstraint(
            "subtotal >= 0",
            name="ck_sale_items_subtotal_nonnegative",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"])
    op.create_index("ix_sale_items_product_id", "sale_items", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_sale_items_product_id", table_name="sale_items")
    op.drop_index("ix_sale_items_sale_id", table_name="sale_items")
    op.drop_table("sale_items")
    op.drop_index("ix_sales_status", table_name="sales")
    op.drop_index("ix_sales_customer_id", table_name="sales")
    op.drop_index("ix_sales_sale_date", table_name="sales")
    op.drop_table("sales")
