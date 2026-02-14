from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from src.core.config import Settings, get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class TokenData(BaseModel):
    sub: str
    exp: int


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
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(UTC).timestamp()),
    }
    return cast(str, jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm))


def decode_access_token(token: str, settings: Settings) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        subject = payload.get("sub")
        exp = payload.get("exp")
        if not isinstance(subject, str) or not isinstance(exp, int):
            raise ValueError("Invalid token payload")
        token_data = TokenData(sub=subject, exp=exp)
        return token_data.sub
    except (JWTError, ValueError) as exc:
        raise _credentials_exception() from exc


def authenticate_predefined_user(username: str, password: str, settings: Settings) -> bool:
    raw_pairs = [item.strip() for item in settings.predefined_users.split(",") if item.strip()]
    for pair in raw_pairs:
        if ":" not in pair:
            continue
        configured_username, configured_password = pair.split(":", 1)
        if username == configured_username.strip() and password == configured_password.strip():
            return True
    return False


async def get_current_subject(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> str:
    return decode_access_token(token, settings)
