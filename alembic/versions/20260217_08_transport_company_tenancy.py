"""add transport company tenancy and admin user mappings

Revision ID: 20260217_08
Revises: 20260216_07
Create Date: 2026-02-17 00:00:00
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_08"
down_revision: str | None = "20260216_07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _predefined_usernames() -> list[str]:
    raw = os.getenv("PREDEFINED_USERS", "admin:secret,mohammed@sikarcargo.com:sikar@123")
    usernames: list[str] = []
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        username = pair.split(":", 1)[0].strip()
        if username and username not in usernames:
            usernames.append(username)
    if not usernames:
        usernames = ["admin"]
    return usernames


def upgrade() -> None:
    connection = op.get_bind()
    now = datetime.now(UTC)

    op.create_table(
        "transport_companies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("trn", sa.String(length=30), nullable=False),
        sa.UniqueConstraint("uuid", name="uq_transport_companies_uuid"),
    )
    op.create_index("ix_transport_companies_uuid", "transport_companies", ["uuid"])

    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("transport_company_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["transport_company_id"],
            ["transport_companies.id"],
            ondelete="CASCADE",
            name="fk_admin_users_transport_company_id_transport_companies",
        ),
        sa.UniqueConstraint("username", name="uq_admin_users_username"),
    )
    op.create_index("ix_admin_users_username", "admin_users", ["username"])
    op.create_index("ix_admin_users_transport_company_id", "admin_users", ["transport_company_id"])

    transport_companies_table = sa.table(
        "transport_companies",
        sa.column("id", sa.Integer()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("uuid", sa.String()),
        sa.column("name", sa.String()),
        sa.column("email", sa.String()),
        sa.column("location", sa.String()),
        sa.column("trn", sa.String()),
    )
    insert_stmt = (
        sa.insert(transport_companies_table)
        .values(
            created_at=now,
            updated_at=now,
            uuid=str(uuid4()),
            name="Sikar Cargo Transport By Heavy & Light Trucks L.L.C",
            email="sikarcargo@gmail.com",
            location="G1 Office, Deira Naif, Dubai, UAE",
            trn="100360756900003",
        )
        .returning(transport_companies_table.c.id)
    )
    default_transport_company_id = int(connection.execute(insert_stmt).scalar_one())

    admin_users_table = sa.table(
        "admin_users",
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("username", sa.String()),
        sa.column("transport_company_id", sa.Integer()),
    )
    for username in _predefined_usernames():
        connection.execute(
            sa.insert(admin_users_table).values(
                created_at=now,
                updated_at=now,
                username=username,
                transport_company_id=default_transport_company_id,
            )
        )

    with op.batch_alter_table("companies") as batch_op:
        batch_op.add_column(sa.Column("transport_company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_companies_transport_company_id", ["transport_company_id"])

    with op.batch_alter_table("trips") as batch_op:
        batch_op.add_column(sa.Column("transport_company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_trips_transport_company_id", ["transport_company_id"])

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.add_column(sa.Column("transport_company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_invoices_transport_company_id", ["transport_company_id"])

    with op.batch_alter_table("drivers") as batch_op:
        batch_op.add_column(sa.Column("transport_company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_drivers_transport_company_id", ["transport_company_id"])

    with op.batch_alter_table("signatories") as batch_op:
        batch_op.add_column(sa.Column("transport_company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_signatories_transport_company_id", ["transport_company_id"])
        batch_op.drop_constraint("uq_signatories_name", type_="unique")

    with op.batch_alter_table("contact_requests") as batch_op:
        batch_op.add_column(sa.Column("transport_company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_contact_requests_transport_company_id", ["transport_company_id"])

    with op.batch_alter_table("quote_requests") as batch_op:
        batch_op.add_column(sa.Column("transport_company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_quote_requests_transport_company_id", ["transport_company_id"])

    for table_name in (
        "companies",
        "trips",
        "invoices",
        "drivers",
        "signatories",
        "contact_requests",
        "quote_requests",
    ):
        connection.execute(
            sa.text(
                f"UPDATE {table_name} SET transport_company_id = :transport_company_id "
                "WHERE transport_company_id IS NULL"
            ),
            {"transport_company_id": default_transport_company_id},
        )

    with op.batch_alter_table("companies") as batch_op:
        batch_op.alter_column("transport_company_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_companies_transport_company_id_transport_companies",
            "transport_companies",
            ["transport_company_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("trips") as batch_op:
        batch_op.alter_column("transport_company_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_trips_transport_company_id_transport_companies",
            "transport_companies",
            ["transport_company_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.alter_column("transport_company_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_invoices_transport_company_id_transport_companies",
            "transport_companies",
            ["transport_company_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("drivers") as batch_op:
        batch_op.alter_column("transport_company_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_drivers_transport_company_id_transport_companies",
            "transport_companies",
            ["transport_company_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("signatories") as batch_op:
        batch_op.alter_column("transport_company_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_signatories_transport_company_id_transport_companies",
            "transport_companies",
            ["transport_company_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_unique_constraint(
            "uq_signatories_transport_company_id_name",
            ["transport_company_id", "name"],
        )

    with op.batch_alter_table("contact_requests") as batch_op:
        batch_op.alter_column("transport_company_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_contact_requests_transport_company_id_transport_companies",
            "transport_companies",
            ["transport_company_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("quote_requests") as batch_op:
        batch_op.alter_column("transport_company_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_quote_requests_transport_company_id_transport_companies",
            "transport_companies",
            ["transport_company_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("quote_requests") as batch_op:
        batch_op.drop_constraint(
            "fk_quote_requests_transport_company_id_transport_companies", type_="foreignkey"
        )
        batch_op.drop_index("ix_quote_requests_transport_company_id")
        batch_op.drop_column("transport_company_id")

    with op.batch_alter_table("contact_requests") as batch_op:
        batch_op.drop_constraint(
            "fk_contact_requests_transport_company_id_transport_companies", type_="foreignkey"
        )
        batch_op.drop_index("ix_contact_requests_transport_company_id")
        batch_op.drop_column("transport_company_id")

    with op.batch_alter_table("signatories") as batch_op:
        batch_op.drop_constraint("uq_signatories_transport_company_id_name", type_="unique")
        batch_op.create_unique_constraint("uq_signatories_name", ["name"])
        batch_op.drop_constraint(
            "fk_signatories_transport_company_id_transport_companies", type_="foreignkey"
        )
        batch_op.drop_index("ix_signatories_transport_company_id")
        batch_op.drop_column("transport_company_id")

    with op.batch_alter_table("drivers") as batch_op:
        batch_op.drop_constraint(
            "fk_drivers_transport_company_id_transport_companies", type_="foreignkey"
        )
        batch_op.drop_index("ix_drivers_transport_company_id")
        batch_op.drop_column("transport_company_id")

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.drop_constraint(
            "fk_invoices_transport_company_id_transport_companies", type_="foreignkey"
        )
        batch_op.drop_index("ix_invoices_transport_company_id")
        batch_op.drop_column("transport_company_id")

    with op.batch_alter_table("trips") as batch_op:
        batch_op.drop_constraint(
            "fk_trips_transport_company_id_transport_companies", type_="foreignkey"
        )
        batch_op.drop_index("ix_trips_transport_company_id")
        batch_op.drop_column("transport_company_id")

    with op.batch_alter_table("companies") as batch_op:
        batch_op.drop_constraint(
            "fk_companies_transport_company_id_transport_companies", type_="foreignkey"
        )
        batch_op.drop_index("ix_companies_transport_company_id")
        batch_op.drop_column("transport_company_id")

    op.drop_index("ix_admin_users_transport_company_id", table_name="admin_users")
    op.drop_index("ix_admin_users_username", table_name="admin_users")
    op.drop_table("admin_users")

    op.drop_index("ix_transport_companies_uuid", table_name="transport_companies")
    op.drop_table("transport_companies")
