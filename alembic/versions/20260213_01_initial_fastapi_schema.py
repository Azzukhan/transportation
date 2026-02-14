"""initial fastapi schema

Revision ID: 20260213_01
Revises:
Create Date: 2026-02-13 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260213_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("contact_person", sa.String(length=25), nullable=False),
        sa.Column("paid_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("unpaid_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("po_box", sa.String(length=20), nullable=False),
    )
    op.create_index("ix_companies_email", "companies", ["email"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("freight", sa.String(length=25), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("vat", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("toll_gate", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("driver", sa.String(length=30), nullable=False),
        sa.Column("paid", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("trips")
    op.drop_table("invoices")
    op.drop_index("ix_companies_email", table_name="companies")
    op.drop_table("companies")
