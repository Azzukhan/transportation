"""add admin refresh token table

Revision ID: 20260217_12
Revises: 20260217_11
Create Date: 2026-02-17 15:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_12"
down_revision: str | None = "20260217_11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("family_id", sa.String(length=36), nullable=False),
        sa.Column("replaced_by_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["admin_user_id"],
            ["admin_users.id"],
            ondelete="CASCADE",
            name="fk_art_admin_user_id_admin_users",
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_id"],
            ["admin_refresh_tokens.id"],
            ondelete="SET NULL",
            name="fk_art_replaced_by_id_admin_refresh_tokens",
        ),
    )
    op.create_index(
        "ix_admin_refresh_tokens_admin_user_id", "admin_refresh_tokens", ["admin_user_id"]
    )
    op.create_index(
        "ix_admin_refresh_tokens_token_hash", "admin_refresh_tokens", ["token_hash"], unique=True
    )
    op.create_index("ix_admin_refresh_tokens_family_id", "admin_refresh_tokens", ["family_id"])


def downgrade() -> None:
    op.drop_index("ix_admin_refresh_tokens_family_id", table_name="admin_refresh_tokens")
    op.drop_index("ix_admin_refresh_tokens_token_hash", table_name="admin_refresh_tokens")
    op.drop_index("ix_admin_refresh_tokens_admin_user_id", table_name="admin_refresh_tokens")
    op.drop_table("admin_refresh_tokens")
