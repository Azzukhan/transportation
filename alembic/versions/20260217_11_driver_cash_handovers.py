"""add driver cash handovers table

Revision ID: 20260217_11
Revises: 20260217_10
Create Date: 2026-02-17 13:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_11"
down_revision: str | None = "20260217_10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "driver_cash_handovers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("transport_company_id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("handover_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["drivers.id"],
            ondelete="CASCADE",
            name="fk_dch_driver_id_drivers",
        ),
        sa.ForeignKeyConstraint(
            ["transport_company_id"],
            ["transport_companies.id"],
            ondelete="CASCADE",
            name="fk_dch_tc_id_transport_companies",
        ),
    )
    op.create_index(
        "ix_driver_cash_handovers_transport_company_id",
        "driver_cash_handovers",
        ["transport_company_id"],
    )
    op.create_index(
        "ix_driver_cash_handovers_driver_id",
        "driver_cash_handovers",
        ["driver_id"],
    )
    op.create_index(
        "ix_driver_cash_handovers_handover_date",
        "driver_cash_handovers",
        ["handover_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_driver_cash_handovers_handover_date", table_name="driver_cash_handovers")
    op.drop_index("ix_driver_cash_handovers_driver_id", table_name="driver_cash_handovers")
    op.drop_index(
        "ix_driver_cash_handovers_transport_company_id", table_name="driver_cash_handovers"
    )
    op.drop_table("driver_cash_handovers")
