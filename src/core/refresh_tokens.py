from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.models.admin_refresh_token import AdminRefreshToken
from src.models.admin_user import AdminUser


class RefreshTokenReuseDetected(Exception):
    pass


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generate_refresh_token_value() -> str:
    return secrets.token_urlsafe(48)


def _utcnow_naive() -> datetime:
    return datetime.utcnow()


async def issue_refresh_token(
    session: AsyncSession,
    *,
    admin_user: AdminUser,
    settings: Settings,
) -> str:
    raw = _generate_refresh_token_value()
    record = AdminRefreshToken(
        admin_user_id=admin_user.id,
        token_hash=hash_refresh_token(raw),
        family_id=str(uuid.uuid4()),
        replaced_by_id=None,
        expires_at=_utcnow_naive() + timedelta(days=settings.refresh_token_expire_days),
        used_at=None,
        revoked_at=None,
    )
    session.add(record)
    await session.commit()
    return raw


async def rotate_refresh_token(
    session: AsyncSession,
    *,
    provided_token: str,
    settings: Settings,
) -> tuple[AdminUser, str]:
    now = _utcnow_naive()
    provided_hash = hash_refresh_token(provided_token)
    stmt: Select[tuple[AdminRefreshToken]] = (
        select(AdminRefreshToken)
        .where(AdminRefreshToken.token_hash == provided_hash)
        .order_by(AdminRefreshToken.id.desc())
    )
    result = await session.execute(stmt)
    token_row = result.scalar_one_or_none()
    if token_row is None:
        raise ValueError("Invalid refresh token")

    if token_row.expires_at <= now:
        token_row.revoked_at = now
        await session.commit()
        raise ValueError("Refresh token expired")

    if token_row.revoked_at is not None or token_row.used_at is not None:
        await _revoke_token_family(session, token_row.family_id)
        raise RefreshTokenReuseDetected("Refresh token reuse detected")

    admin_user = await session.get(AdminUser, token_row.admin_user_id)
    if admin_user is None:
        token_row.revoked_at = now
        await session.commit()
        raise ValueError("Refresh token user not found")

    new_raw = _generate_refresh_token_value()
    new_row = AdminRefreshToken(
        admin_user_id=admin_user.id,
        token_hash=hash_refresh_token(new_raw),
        family_id=token_row.family_id,
        replaced_by_id=None,
        expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        used_at=None,
        revoked_at=None,
    )
    session.add(new_row)
    await session.flush()

    token_row.used_at = now
    token_row.revoked_at = now
    token_row.replaced_by_id = new_row.id
    await session.commit()
    return admin_user, new_raw


async def revoke_all_refresh_tokens_for_user(session: AsyncSession, *, admin_user_id: int) -> int:
    now = _utcnow_naive()
    stmt: Select[tuple[AdminRefreshToken]] = select(AdminRefreshToken).where(
        AdminRefreshToken.admin_user_id == admin_user_id,
        AdminRefreshToken.revoked_at.is_(None),
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    for item in rows:
        item.revoked_at = now
    await session.commit()
    return len(rows)


async def _revoke_token_family(session: AsyncSession, family_id: str) -> None:
    now = _utcnow_naive()
    stmt: Select[tuple[AdminRefreshToken]] = select(AdminRefreshToken).where(
        AdminRefreshToken.family_id == family_id,
        AdminRefreshToken.revoked_at.is_(None),
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    for item in rows:
        item.revoked_at = now
    await session.commit()
