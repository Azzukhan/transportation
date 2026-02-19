"""add trn column to companies

Revision ID: 20260215_04
Revises: 20260213_03
Create Date: 2026-02-15 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_04"
down_revision: str | None = "20260213_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("trn", sa.String(length=30), nullable=False, server_default=""),
    )
    op.alter_column("companies", "trn", server_default=None)


def downgrade() -> None:
    op.drop_column("companies", "trn")
