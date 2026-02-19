import pytest
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
async def test_create_and_list_companies(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    payload = {
        "name": "Acme",
        "address": "Main St",
        "email": "ops@acme.example.com",
        "phone": "123",
        "trn": "100000000000001",
        "contact_person": "Alex",
        "po_box": "100",
    }
    create_response = await client.post("/api/v1/companies", json=payload, headers=headers)
    assert create_response.status_code == 201

    list_response = await client.get("/api/v1/companies", headers=headers)
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Acme"
