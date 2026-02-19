import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_me_and_refresh_rotation_with_reuse_detection(client: AsyncClient) -> None:
    login = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    assert login.status_code == 200
    refresh_token = login.cookies.get("refresh_token")
    assert isinstance(refresh_token, str) and refresh_token
    assert login.cookies.get("access_token")
    assert login.cookies.get("refresh_token")
    csrf_token = login.cookies.get("csrf_token")
    assert isinstance(csrf_token, str) and csrf_token

    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "admin"

    rotated = await client.post(
        "/api/v1/auth/token/refresh",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert rotated.status_code == 200
    new_refresh_token = rotated.cookies.get("refresh_token")
    assert isinstance(new_refresh_token, str) and new_refresh_token
    assert new_refresh_token != refresh_token
    new_csrf_token = rotated.cookies.get("csrf_token")
    assert isinstance(new_csrf_token, str) and new_csrf_token

    reused_old = await client.post(
        "/api/v1/auth/token/refresh",
        json={"refresh_token": refresh_token},
        headers={"X-CSRF-Token": new_csrf_token},
    )
    assert reused_old.status_code == 401
    assert "reuse detected" in reused_old.json()["error"]["message"].lower()

    # Reuse detection should revoke the family, including the rotated token.
    family_revoked = await client.post(
        "/api/v1/auth/token/refresh",
        json={"refresh_token": new_refresh_token},
        headers={"X-CSRF-Token": new_csrf_token},
    )
    assert family_revoked.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_tokens(client: AsyncClient) -> None:
    login = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    assert login.status_code == 200
    refresh_token = login.cookies.get("refresh_token")
    assert isinstance(refresh_token, str) and refresh_token
    csrf_token = login.cookies.get("csrf_token")
    assert isinstance(csrf_token, str) and csrf_token

    logout = await client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert logout.status_code == 204

    refresh_after_logout = await client.post(
        "/api/v1/auth/token/refresh",
        json={"refresh_token": refresh_token},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert refresh_after_logout.status_code == 401


@pytest.mark.asyncio
async def test_logout_invalidates_existing_access_token(client: AsyncClient) -> None:
    login = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    assert login.status_code == 200
    access_token = login.cookies.get("access_token")
    csrf_token = login.cookies.get("csrf_token")
    assert isinstance(access_token, str) and access_token
    assert isinstance(csrf_token, str) and csrf_token

    logout = await client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert logout.status_code == 204

    stale_access = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert stale_access.status_code == 401


@pytest.mark.asyncio
async def test_cookie_authenticated_unsafe_request_requires_csrf(client: AsyncClient) -> None:
    login = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    assert login.status_code == 200

    forbidden = await client.post(
        "/api/v1/auth/logout",
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "csrf_invalid"
