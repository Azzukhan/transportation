"""store signature images in database blobs

Revision ID: 20260215_06
Revises: 20260215_05
Create Date: 2026-02-15 17:40:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_06"
down_revision: str | None = "20260215_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("signatories") as batch_op:
        batch_op.alter_column(
            "signature_image_path", existing_type=sa.String(length=255), nullable=True
        )
        batch_op.add_column(sa.Column("signature_image_mime", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("signature_image_data", sa.LargeBinary(), nullable=True))

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.add_column(sa.Column("signatory_image_mime", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("signatory_image_data", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("invoices") as batch_op:
        batch_op.drop_column("signatory_image_data")
        batch_op.drop_column("signatory_image_mime")

    with op.batch_alter_table("signatories") as batch_op:
        batch_op.drop_column("signature_image_data")
        batch_op.drop_column("signature_image_mime")
        batch_op.alter_column(
            "signature_image_path", existing_type=sa.String(length=255), nullable=False
        )
