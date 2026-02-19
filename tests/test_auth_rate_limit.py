import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_username_lockout_after_failed_attempts(client: AsyncClient) -> None:
    for _ in range(4):
        response = await client.post(
            "/api/v1/auth/token",
            json={"username": "admin", "password": "wrong-password"},
        )
        assert response.status_code == 401

    lockout = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "wrong-password"},
    )
    assert lockout.status_code == 429
    assert "Too many failed login attempts for this username" in lockout.json()["error"]["message"]
    assert int(lockout.headers["retry-after"]) > 0

    blocked_correct_password = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    assert blocked_correct_password.status_code == 429
    assert "Try again in" in blocked_correct_password.json()["error"]["message"]


@pytest.mark.asyncio
async def test_auth_ip_rate_limit_blocks_excess_attempts(client: AsyncClient) -> None:
    for i in range(20):
        response = await client.post(
            "/api/v1/auth/token",
            json={"username": f"unknown-{i}", "password": "wrong-password"},
        )
        assert response.status_code == 401

    blocked = await client.post(
        "/api/v1/auth/token",
        json={"username": "another-user", "password": "wrong-password"},
    )
    assert blocked.status_code == 429
    assert "Too many login attempts from this IP address" in blocked.json()["error"]["message"]
    assert int(blocked.headers["retry-after"]) > 0
