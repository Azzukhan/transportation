"""add password hash to admin users and backfill from env

Revision ID: 20260217_09
Revises: 20260217_08
Create Date: 2026-02-17 00:30:00
"""

from __future__ import annotations

import base64
import hashlib
import os
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_09"
down_revision: str | None = "20260217_08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _hash_password(password: str) -> str:
    iterations = 390000
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt_b64}${digest_b64}"


def _predefined_credentials() -> dict[str, str]:
    raw = os.getenv("PREDEFINED_USERS", "admin:secret,mohammed@sikarcargo.com:sikar@123")
    creds: dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        username, password = pair.split(":", 1)
        username = username.strip()
        if username:
            creds[username] = password.strip()
    return creds


def upgrade() -> None:
    connection = op.get_bind()
    op.add_column("admin_users", sa.Column("password_hash", sa.String(length=255), nullable=True))

    credentials = _predefined_credentials()
    rows = connection.execute(sa.text("SELECT id, username FROM admin_users")).fetchall()
    for row in rows:
        username = row.username
        password = credentials.get(username, "secret")
        connection.execute(
            sa.text("UPDATE admin_users SET password_hash = :password_hash WHERE id = :id"),
            {"password_hash": _hash_password(password), "id": row.id},
        )

    with op.batch_alter_table("admin_users") as batch_op:
        batch_op.alter_column("password_hash", existing_type=sa.String(length=255), nullable=False)


def downgrade() -> None:
    op.drop_column("admin_users", "password_hash")
