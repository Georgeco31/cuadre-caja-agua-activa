"""create suppliers and purchases

Revision ID: 0019_purchases
Revises: 0018_route_receipts
Create Date: 2026-07-23
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0019_purchases"
down_revision: str | None = "0018_route_receipts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("identification", sa.String(length=80), nullable=True),
        sa.Column("primary_phone", sa.String(length=50), nullable=True),
        sa.Column("secondary_phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("supplier_type", sa.String(length=80), nullable=True),
        sa.Column("payment_terms", sa.String(length=120), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
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
            "length(trim(name)) > 0",
            name="ck_suppliers_name_not_blank",
        ),
        sa.CheckConstraint(
            "identification IS NULL OR length(trim(identification)) > 0",
            name="ck_suppliers_identification_not_blank",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identification"),
    )
    op.create_index(
        "ix_suppliers_identification",
        "suppliers",
        ["identification"],
    )
    op.create_index("ix_suppliers_supplier_type", "suppliers", ["supplier_type"])
    op.create_index("ix_suppliers_is_active", "suppliers", ["is_active"])

    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("purchase_number", sa.String(length=80), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("document_number", sa.String(length=120), nullable=True),
        sa.Column("document_type", sa.String(length=50), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column(
            "payment_status",
            sa.String(length=20),
            server_default=sa.text("'unpaid'"),
            nullable=False,
        ),
        sa.Column(
            "subtotal_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "discount_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "tax_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "total_amount",
            sa.Numeric(precision=14, scale=2),
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
            "length(trim(purchase_number)) > 0",
            name="ck_purchases_number_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_purchases_status",
        ),
        sa.CheckConstraint(
            "payment_status IN ('unpaid', 'partial', 'paid')",
            name="ck_purchases_payment_status",
        ),
        sa.CheckConstraint(
            "subtotal_amount >= 0 AND discount_amount >= 0 "
            "AND tax_amount >= 0 AND total_amount >= 0",
            name="ck_purchases_amounts_nonnegative",
        ),
        sa.CheckConstraint(
            "total_amount = subtotal_amount + tax_amount",
            name="ck_purchases_total",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_purchases_void_state",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("purchase_number"),
    )
    for index_name, column_name in (
        ("ix_purchases_purchase_number", "purchase_number"),
        ("ix_purchases_supplier_id", "supplier_id"),
        ("ix_purchases_purchase_date", "purchase_date"),
        ("ix_purchases_document_number", "document_number"),
        ("ix_purchases_status", "status"),
        ("ix_purchases_payment_status", "payment_status"),
    ):
        op.create_index(index_name, "purchases", [column_name])

    op.create_table(
        "purchase_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("purchase_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("product_sku_snapshot", sa.String(length=80), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=255), nullable=True),
        sa.Column(
            "product_presentation_snapshot",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(precision=12, scale=3),
            nullable=False,
        ),
        sa.Column(
            "unit_cost",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "discount_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "tax_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "subtotal_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
        ),
        sa.Column(
            "total_amount",
            sa.Numeric(precision=14, scale=2),
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
            "product_id IS NOT NULL OR "
            "(description IS NOT NULL AND length(trim(description)) > 0)",
            name="ck_purchase_items_product_or_description",
        ),
        sa.CheckConstraint(
            "product_id IS NULL OR "
            "(product_name_snapshot IS NOT NULL "
            "AND length(trim(product_name_snapshot)) > 0)",
            name="ck_purchase_items_product_snapshot",
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_purchase_items_quantity_positive",
        ),
        sa.CheckConstraint(
            "unit_cost >= 0 AND discount_amount >= 0 AND tax_amount >= 0 "
            "AND subtotal_amount >= 0 AND total_amount >= 0",
            name="ck_purchase_items_amounts_nonnegative",
        ),
        sa.CheckConstraint(
            "subtotal_amount = round(quantity * unit_cost - discount_amount, 2)",
            name="ck_purchase_items_subtotal",
        ),
        sa.CheckConstraint(
            "total_amount = subtotal_amount + tax_amount",
            name="ck_purchase_items_total",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["purchase_id"], ["purchases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_purchase_items_purchase_id",
        "purchase_items",
        ["purchase_id"],
    )
    op.create_index(
        "ix_purchase_items_product_id",
        "purchase_items",
        ["product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_purchase_items_product_id", table_name="purchase_items")
    op.drop_index("ix_purchase_items_purchase_id", table_name="purchase_items")
    op.drop_table("purchase_items")

    for index_name in (
        "ix_purchases_payment_status",
        "ix_purchases_status",
        "ix_purchases_document_number",
        "ix_purchases_purchase_date",
        "ix_purchases_supplier_id",
        "ix_purchases_purchase_number",
    ):
        op.drop_index(index_name, table_name="purchases")
    op.drop_table("purchases")

    op.drop_index("ix_suppliers_is_active", table_name="suppliers")
    op.drop_index("ix_suppliers_supplier_type", table_name="suppliers")
    op.drop_index("ix_suppliers_identification", table_name="suppliers")
    op.drop_table("suppliers")
