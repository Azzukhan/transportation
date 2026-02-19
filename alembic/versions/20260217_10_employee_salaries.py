"""add employee salaries table

Revision ID: 20260217_10
Revises: 20260217_09
Create Date: 2026-02-17 10:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_10"
down_revision: str | None = "20260217_09"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employee_salaries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("transport_company_id", sa.Integer(), nullable=False),
        sa.Column("employee_name", sa.String(length=255), nullable=False),
        sa.Column("work_permit_no", sa.String(length=8), nullable=False),
        sa.Column("personal_no", sa.String(length=14), nullable=False),
        sa.Column("bank_name_routing_no", sa.String(length=255), nullable=True),
        sa.Column("bank_account_no", sa.String(length=50), nullable=False),
        sa.Column("days_absent", sa.Integer(), nullable=True),
        sa.Column("fixed_portion", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("variable_portion", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("total_payment", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("on_leave", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["transport_company_id"],
            ["transport_companies.id"],
            ondelete="CASCADE",
            name="fk_employee_salaries_transport_company_id_transport_companies",
        ),
    )
    op.create_index(
        "ix_employee_salaries_transport_company_id",
        "employee_salaries",
        ["transport_company_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_employee_salaries_transport_company_id", table_name="employee_salaries")
    op.drop_table("employee_salaries")
