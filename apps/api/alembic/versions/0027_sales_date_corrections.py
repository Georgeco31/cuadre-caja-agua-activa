"""Create audited sale date corrections.

Revision ID: 0027_sale_date_corrections
Revises: 0026_user_roles
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0027_sale_date_corrections"
down_revision: str | None = "0026_user_roles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sale_date_corrections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column(
            "correction_type",
            sa.String(length=30),
            server_default="date_change",
            nullable=False,
        ),
        sa.Column("previous_sale_date", sa.Date(), nullable=False),
        sa.Column("new_sale_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "correction_type = 'date_change'",
            name="ck_sale_date_corrections_type",
        ),
        sa.CheckConstraint(
            "previous_sale_date <> new_sale_date",
            name="ck_sale_date_corrections_dates_different",
        ),
        sa.CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_sale_date_corrections_reason_not_blank",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sale_date_corrections_created_by"),
        "sale_date_corrections",
        ["created_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sale_date_corrections_sale_id"),
        "sale_date_corrections",
        ["sale_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_sale_date_corrections_sale_id"),
        table_name="sale_date_corrections",
    )
    op.drop_index(
        op.f("ix_sale_date_corrections_created_by"),
        table_name="sale_date_corrections",
    )
    op.drop_table("sale_date_corrections")
