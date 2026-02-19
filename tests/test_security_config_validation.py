from __future__ import annotations

import pytest
from jose import jwt

from src.core.auth import decode_access_token
from src.core.config import Settings, get_settings
from src.main import create_app


def _valid_signature_keys() -> str:
    # base64(32-byte keys)
    return (
        "k1:MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=,"
        "k2:ZmVkY2JhOTg3NjU0MzIxMGZlZGNiYTk4NzY1NDMyMTA="
    )


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


def test_production_rejects_weak_or_default_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("SECRET_KEY", "dev-only-change-me")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://admin.example.com")
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "true")
    monkeypatch.setenv("SIGNATURE_ENCRYPTION_ENABLED", "true")
    monkeypatch.setenv("SIGNATURE_ENCRYPTION_KEYS", _valid_signature_keys())
    monkeypatch.setenv("SIGNATURE_ACTIVE_KEY_ID", "k1")
    monkeypatch.setenv("AUDIT_HASH_KEY", "x" * 40)
    with pytest.raises(ValueError, match="SECRET_KEY"):
        create_app()


def test_production_rejects_insecure_cookie_and_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./db.sqlite3")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://admin.example.com")
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")
    monkeypatch.setenv("SIGNATURE_ENCRYPTION_ENABLED", "true")
    monkeypatch.setenv("SIGNATURE_ENCRYPTION_KEYS", _valid_signature_keys())
    monkeypatch.setenv("SIGNATURE_ACTIVE_KEY_ID", "k1")
    monkeypatch.setenv("AUDIT_HASH_KEY", "y" * 48)
    with pytest.raises(ValueError):
        create_app()


def test_production_accepts_hardened_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "x" * 64)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://admin.example.com,https://ops.example.com")
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "true")
    monkeypatch.setenv("SIGNATURE_ENCRYPTION_ENABLED", "true")
    monkeypatch.setenv("SIGNATURE_ENCRYPTION_KEYS", _valid_signature_keys())
    monkeypatch.setenv("SIGNATURE_ACTIVE_KEY_ID", "k2")
    monkeypatch.setenv("AUDIT_HASH_KEY", "z" * 64)
    monkeypatch.setenv("SENSITIVE_EXPORT_STEP_UP_REQUIRED", "true")
    monkeypatch.setenv("SENSITIVE_EXPORT_STEP_UP_TOKEN", "s" * 40)
    app = create_app()
    assert app.title == "transportation-api"


def test_decode_access_token_accepts_previous_jwt_keys() -> None:
    old_key = "old-key-" + ("a" * 32)
    new_key = "new-key-" + ("b" * 32)
    token = jwt.encode({"sub": "admin", "exp": 4102444800}, old_key, algorithm="HS256")

    settings = Settings(
        secret_key=new_key,
        jwt_previous_secret_keys=old_key,
        signature_encryption_keys=_valid_signature_keys(),
        signature_active_key_id="k1",
    )
    token_data = decode_access_token(token, settings)
    assert token_data.sub == "admin"
