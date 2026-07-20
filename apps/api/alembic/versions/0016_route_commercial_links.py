"""link sales and payments to route loads

Revision ID: 0016_route_links
Revises: 0015_route_returns
Create Date: 2026-07-19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0016_route_links"
down_revision: str | None = "0015_route_returns"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column("route_load_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_sales_route_load_id",
        "sales",
        "route_loads",
        ["route_load_id"],
        ["id"],
    )
    op.create_index("ix_sales_route_load_id", "sales", ["route_load_id"])

    op.add_column(
        "credit_payments",
        sa.Column("route_load_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_credit_payments_route_load_id",
        "credit_payments",
        "route_loads",
        ["route_load_id"],
        ["id"],
    )
    op.create_index(
        "ix_credit_payments_route_load_id",
        "credit_payments",
        ["route_load_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_credit_payments_route_load_id", table_name="credit_payments")
    op.drop_constraint(
        "fk_credit_payments_route_load_id",
        "credit_payments",
        type_="foreignkey",
    )
    op.drop_column("credit_payments", "route_load_id")

    op.drop_index("ix_sales_route_load_id", table_name="sales")
    op.drop_constraint(
        "fk_sales_route_load_id",
        "sales",
        type_="foreignkey",
    )
    op.drop_column("sales", "route_load_id")
