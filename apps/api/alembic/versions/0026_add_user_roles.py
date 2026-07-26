"""add user roles

Revision ID: 0026_user_roles
Revises: 0025_materials
Create Date: 2026-07-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0026_user_roles"
down_revision: str | None = "0025_materials"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=30),
            server_default=sa.text("'admin_auditor'"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('operator', 'admin_auditor')",
    )
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=30),
        server_default=sa.text("'operator'"),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "role")
