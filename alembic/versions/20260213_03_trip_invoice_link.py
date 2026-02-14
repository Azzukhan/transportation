"""add trip invoice linkage

Revision ID: 20260213_03
Revises: 20260213_02
Create Date: 2026-02-13 01:10:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260213_03"
down_revision: str | None = "20260213_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("trips") as batch_op:
        batch_op.add_column(sa.Column("invoice_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_trips_invoice_id_invoices",
            "invoices",
            ["invoice_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("trips") as batch_op:
        batch_op.drop_constraint("fk_trips_invoice_id_invoices", type_="foreignkey")
        batch_op.drop_column("invoice_id")
