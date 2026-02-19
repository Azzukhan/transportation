"""add invoice custom numbers and signatories

Revision ID: 20260215_05
Revises: 20260215_04
Create Date: 2026-02-15 02:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_05"
down_revision: str | None = "20260215_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "signatories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("signature_image_path", sa.String(length=255), nullable=False, server_default=""),
    )

    op.bulk_insert(
        sa.table(
            "signatories",
            sa.column("name", sa.String),
            sa.column("signature_image_path", sa.String),
        ),
        [
            {"name": "Roshan", "signature_image_path": "signatures/roshan.svg"},
            {"name": "Aslam", "signature_image_path": "signatures/aslam.svg"},
            {"name": "Javed", "signature_image_path": "signatures/javed.svg"},
            {"name": "Ashfak", "signature_image_path": "signatures/ashfak.svg"},
            {"name": "Altaf", "signature_image_path": "signatures/altaf.svg"},
        ],
    )

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.add_column(sa.Column("invoice_number", sa.String(length=60), nullable=True))
        batch_op.add_column(
            sa.Column(
                "prepared_by_mode",
                sa.String(length=25),
                nullable=False,
                server_default="without_signature",
            )
        )
        batch_op.add_column(sa.Column("signatory_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("signatory_name", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("signatory_image_path", sa.String(length=255), nullable=True))
        batch_op.create_foreign_key(
            "fk_invoices_signatory_id_signatories",
            "signatories",
            ["signatory_id"],
            ["id"],
            ondelete="SET NULL",
        )

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.alter_column("prepared_by_mode", server_default=None)

    with op.batch_alter_table("signatories") as batch_op:
        batch_op.alter_column("signature_image_path", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("invoices") as batch_op:
        batch_op.drop_constraint("fk_invoices_signatory_id_signatories", type_="foreignkey")
        batch_op.drop_column("signatory_image_path")
        batch_op.drop_column("signatory_name")
        batch_op.drop_column("signatory_id")
        batch_op.drop_column("prepared_by_mode")
        batch_op.drop_column("invoice_number")

    op.drop_table("signatories")
