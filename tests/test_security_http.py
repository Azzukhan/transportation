import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.core.config import get_settings
from src.main import create_app


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "content-security-policy" in response.headers


@pytest.mark.asyncio
async def test_hsts_not_set_in_development(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert "strict-transport-security" not in response.headers


@pytest.mark.asyncio
async def test_hsts_set_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://admin.example.com")
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "true")
    monkeypatch.setenv(
        "SIGNATURE_ENCRYPTION_KEYS",
        "k1:MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=,k2:ZmVkY2JhOTg3NjU0MzIxMGZlZGNiYTk4NzY1NDMyMTA=",
    )
    monkeypatch.setenv("SIGNATURE_ACTIVE_KEY_ID", "k1")
    monkeypatch.setenv("AUDIT_HASH_KEY", "a" * 48)
    app: FastAPI = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://test"
    ) as test_client:
        response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.headers["strict-transport-security"].startswith("max-age=")


@pytest.mark.asyncio
async def test_cors_allows_only_configured_origin(client: AsyncClient) -> None:
    allowed = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.status_code in {200, 204}
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:8080"

    blocked = await client.options(
        "/health",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert blocked.headers.get("access-control-allow-origin") is None
