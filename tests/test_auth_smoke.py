import pytest
from httpx import AsyncClient

from src.core.auth import decode_access_token
from src.core.config import get_settings


@pytest.mark.asyncio
async def test_auth_token_issue_and_decode(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    subject = decode_access_token(body["access_token"], get_settings())
    assert subject == "admin"
