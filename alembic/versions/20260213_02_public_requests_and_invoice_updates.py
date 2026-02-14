"""add public request tables and invoice workflow fields

Revision ID: 20260213_02
Revises: 20260213_01
Create Date: 2026-02-13 00:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260213_02"
down_revision: str | None = "20260213_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contact_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("subject", sa.String(length=160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("source_page", sa.String(length=40), nullable=False, server_default="contact"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_contact_requests_email", "contact_requests", ["email"])

    op.create_table(
        "quote_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("mobile", sa.String(length=40), nullable=False),
        sa.Column("freight", sa.String(length=30), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_quote_requests_email", "quote_requests", ["email"])

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.add_column(sa.Column("due_date", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("format_key", sa.String(length=50), nullable=False, server_default="standard"))
        batch_op.add_column(sa.Column("notes", sa.Text(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True))

    op.execute("UPDATE invoices SET due_date = end_date WHERE due_date IS NULL")

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.alter_column("due_date", existing_type=sa.Date(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("invoices") as batch_op:
        batch_op.drop_column("paid_at")
        batch_op.drop_column("notes")
        batch_op.drop_column("format_key")
        batch_op.drop_column("due_date")

    op.drop_index("ix_quote_requests_email", table_name="quote_requests")
    op.drop_table("quote_requests")

    op.drop_index("ix_contact_requests_email", table_name="contact_requests")
    op.drop_table("contact_requests")
