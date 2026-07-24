"""create price lists

Revision ID: 0020_price_lists
Revises: 0019_purchases
Create Date: 2026-07-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0020_price_lists"
down_revision: str | None = "0019_purchases"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "price_lists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("list_type", sa.String(length=30), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("route_id", sa.Integer(), nullable=True),
        sa.Column(
            "priority",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
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
            name="ck_price_lists_name_not_blank",
        ),
        sa.CheckConstraint(
            "list_type IN "
            "('general', 'customer', 'route', 'customer_route', 'special')",
            name="ck_price_lists_type",
        ),
        sa.CheckConstraint(
            "list_type <> 'customer' OR customer_id IS NOT NULL",
            name="ck_price_lists_customer_target",
        ),
        sa.CheckConstraint(
            "list_type <> 'route' OR route_id IS NOT NULL",
            name="ck_price_lists_route_target",
        ),
        sa.CheckConstraint(
            "list_type <> 'customer_route' OR "
            "(customer_id IS NOT NULL AND route_id IS NOT NULL)",
            name="ck_price_lists_customer_route_target",
        ),
        sa.CheckConstraint(
            "valid_from IS NULL OR valid_to IS NULL OR valid_from <= valid_to",
            name="ck_price_lists_valid_dates",
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["delivery_routes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for index_name, column_name in (
        ("ix_price_lists_list_type", "list_type"),
        ("ix_price_lists_customer_id", "customer_id"),
        ("ix_price_lists_route_id", "route_id"),
        ("ix_price_lists_is_active", "is_active"),
    ):
        op.create_index(index_name, "price_lists", [column_name])

    op.create_table(
        "price_list_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("price_list_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column(
            "unit_price",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "min_quantity",
            sa.Numeric(precision=12, scale=3),
            server_default=sa.text("1.000"),
            nullable=False,
        ),
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
            "unit_price >= 0",
            name="ck_price_list_items_price_nonnegative",
        ),
        sa.CheckConstraint(
            "min_quantity > 0",
            name="ck_price_list_items_min_quantity_positive",
        ),
        sa.ForeignKeyConstraint(["price_list_id"], ["price_lists.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for index_name, column_name in (
        ("ix_price_list_items_price_list_id", "price_list_id"),
        ("ix_price_list_items_product_id", "product_id"),
        ("ix_price_list_items_is_active", "is_active"),
    ):
        op.create_index(index_name, "price_list_items", [column_name])

    op.add_column(
        "sale_items",
        sa.Column("price_source", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "sale_items",
        sa.Column("price_list_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "sale_items",
        sa.Column(
            "price_list_name_snapshot",
            sa.String(length=255),
            nullable=True,
        ),
    )
    op.add_column(
        "sale_items",
        sa.Column("pricing_note", sa.Text(), nullable=True),
    )
    op.create_check_constraint(
        "ck_sale_items_price_source",
        "sale_items",
        "price_source IS NULL OR price_source IN "
        "('default', 'general', 'special', 'customer', 'route', "
        "'customer_route', 'manual')",
    )
    op.create_foreign_key(
        "fk_sale_items_price_list_id_price_lists",
        "sale_items",
        "price_lists",
        ["price_list_id"],
        ["id"],
    )
    op.create_index(
        "ix_sale_items_price_list_id",
        "sale_items",
        ["price_list_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_sale_items_price_list_id", table_name="sale_items")
    op.drop_constraint(
        "fk_sale_items_price_list_id_price_lists",
        "sale_items",
        type_="foreignkey",
    )
    op.drop_constraint(
        "ck_sale_items_price_source",
        "sale_items",
        type_="check",
    )
    op.drop_column("sale_items", "pricing_note")
    op.drop_column("sale_items", "price_list_name_snapshot")
    op.drop_column("sale_items", "price_list_id")
    op.drop_column("sale_items", "price_source")

    op.drop_index(
        "ix_price_list_items_is_active",
        table_name="price_list_items",
    )
    op.drop_index(
        "ix_price_list_items_product_id",
        table_name="price_list_items",
    )
    op.drop_index(
        "ix_price_list_items_price_list_id",
        table_name="price_list_items",
    )
    op.drop_table("price_list_items")

    op.drop_index("ix_price_lists_is_active", table_name="price_lists")
    op.drop_index("ix_price_lists_route_id", table_name="price_lists")
    op.drop_index("ix_price_lists_customer_id", table_name="price_lists")
    op.drop_index("ix_price_lists_list_type", table_name="price_lists")
    op.drop_table("price_lists")
