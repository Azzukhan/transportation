"""add drivers and extend trips for category and driver references

Revision ID: 20260216_07
Revises: 20260215_06
Create Date: 2026-02-16 12:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260216_07"
down_revision: str | None = "20260215_06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("mobile_number", sa.String(length=25), nullable=False),
        sa.Column("passport_number", sa.String(length=40), nullable=True),
        sa.Column("emirates_id_number", sa.String(length=40), nullable=True),
        sa.Column("emirates_id_expiry_date", sa.Date(), nullable=True),
    )

    with op.batch_alter_table("trips") as batch_op:
        batch_op.add_column(
            sa.Column("destination_company_name", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "trip_category", sa.String(length=20), nullable=False, server_default="domestic"
            )
        )
        batch_op.add_column(sa.Column("driver_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("external_driver_name", sa.String(length=120), nullable=True))
        batch_op.add_column(
            sa.Column("external_driver_mobile", sa.String(length=25), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_trips_driver_id_drivers",
            "drivers",
            ["driver_id"],
            ["id"],
            ondelete="SET NULL",
        )

    with op.batch_alter_table("trips") as batch_op:
        batch_op.alter_column("trip_category", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("trips") as batch_op:
        batch_op.drop_constraint("fk_trips_driver_id_drivers", type_="foreignkey")
        batch_op.drop_column("external_driver_mobile")
        batch_op.drop_column("external_driver_name")
        batch_op.drop_column("driver_id")
        batch_op.drop_column("trip_category")
        batch_op.drop_column("destination_company_name")

    op.drop_table("drivers")
