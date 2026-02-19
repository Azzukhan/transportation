import pytest
from fastapi import FastAPI
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    token_response = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    token = token_response.cookies.get("access_token")
    assert token
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_global_rate_limit_returns_429(client: AsyncClient, app: FastAPI) -> None:
    limiter = app.state.request_rate_limiter
    limiter.global_max_requests = 2
    limiter.auth_max_requests = 50
    limiter.upload_max_requests = 50
    limiter.export_max_requests = 50

    payload = {
        "name": "Rate",
        "email": "rate@example.com",
        "phone": "+971551230001",
        "subject": "Global limit",
        "message": "testing global rate limit",
    }
    tenant_headers = {"X-Transport-Company-UUID": "00000000-0000-0000-0000-000000000001"}
    first = await client.post(
        "/api/v1/public/contact-requests", json=payload, headers=tenant_headers
    )
    second = await client.post(
        "/api/v1/public/contact-requests", json=payload, headers=tenant_headers
    )
    third = await client.post(
        "/api/v1/public/contact-requests", json=payload, headers=tenant_headers
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 429
    assert third.json()["error"]["code"] == "rate_limited"
    assert "Retry-After" in third.headers


@pytest.mark.asyncio
async def test_auth_route_rate_limit_returns_429(client: AsyncClient, app: FastAPI) -> None:
    limiter = app.state.request_rate_limiter
    limiter.global_max_requests = 100
    limiter.auth_max_requests = 1

    first = await client.post("/api/v1/auth/token", json={"username": "admin", "password": "wrong"})
    second = await client.post(
        "/api/v1/auth/token", json={"username": "admin", "password": "wrong"}
    )

    assert first.status_code == 401
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "rate_limited"


@pytest.mark.asyncio
async def test_auth_payload_too_large_returns_413(client: AsyncClient, app: FastAPI) -> None:
    settings = app.state.settings
    settings.max_auth_body_bytes = 40
    large_payload = b'{"username":"admin","password":"' + (b"x" * 200) + b'"}'

    response = await client.post(
        "/api/v1/auth/token",
        content=large_payload,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


@pytest.mark.asyncio
async def test_upload_payload_too_large_returns_413(client: AsyncClient, app: FastAPI) -> None:
    settings = app.state.settings
    settings.max_upload_body_bytes = 200
    headers = await _auth_headers(client)

    response = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Big Upload"},
        files={"file": ("signature.png", b"x" * 2048, "image/png")},
        headers=headers,
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"
