import hashlib
import hmac
import os
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings, get_settings
from src.db.session import get_db_session
from src.models.admin_user import AdminUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


class TokenData(BaseModel):
    sub: str
    exp: int
    tv: int = 0


class CurrentAdminContext(BaseModel):
    username: str
    transport_company_id: int


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(
    subject: str,
    settings: Settings,
    expires_delta: timedelta | None = None,
    token_version: int = 0,
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(UTC).timestamp()),
        "tv": token_version,
    }
    return cast(str, jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm))


def decode_access_token(token: str, settings: Settings) -> TokenData:
    last_error: Exception | None = None
    for decode_key in settings.jwt_decode_secret_keys:
        try:
            payload = jwt.decode(
                token,
                decode_key,
                algorithms=[settings.jwt_algorithm],
            )
            subject = payload.get("sub")
            exp = payload.get("exp")
            token_version = payload.get("tv", 0)
            if not isinstance(subject, str) or not isinstance(exp, int):
                raise ValueError("Invalid token payload")
            if not isinstance(token_version, int):
                raise ValueError("Invalid token payload")
            return TokenData(sub=subject, exp=exp, tv=token_version)
        except (JWTError, ValueError) as exc:
            last_error = exc
            continue
    raise _credentials_exception() from last_error


def hash_password(password: str) -> str:
    iterations = 390000
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = urlsafe_b64encode(salt).decode("ascii")
    digest_b64 = urlsafe_b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt_b64}${digest_b64}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algo, iter_str, salt_b64, digest_b64 = password_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iter_str)
        salt = urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = urlsafe_b64decode(digest_b64.encode("ascii"))
    except Exception:
        return False

    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(computed, expected)


async def authenticate_admin_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> bool:
    stmt: Select[tuple[AdminUser]] = select(AdminUser).where(AdminUser.username == username)
    result = await session.execute(stmt)
    admin_user = result.scalar_one_or_none()
    if admin_user is None:
        return False
    return verify_password(password, admin_user.password_hash)


async def get_current_subject(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> str:
    candidate = token or request.cookies.get(settings.auth_access_cookie_name)
    if not candidate:
        raise _credentials_exception()
    return decode_access_token(candidate, settings).sub


async def get_current_admin_context(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    token: str | None = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> CurrentAdminContext:
    candidate = token or request.cookies.get(settings.auth_access_cookie_name)
    if not candidate:
        raise _credentials_exception()
    token_data = decode_access_token(candidate, settings)
    stmt: Select[tuple[AdminUser]] = select(AdminUser).where(AdminUser.username == token_data.sub)
    result = await session.execute(stmt)
    admin_user = result.scalar_one_or_none()

    if admin_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not mapped to any transport company",
        )
    if admin_user.token_version != token_data.tv:
        raise _credentials_exception()

    return CurrentAdminContext(
        username=admin_user.username,
        transport_company_id=admin_user.transport_company_id,
    )
