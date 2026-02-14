import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    token_response = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_list_contact_requests(client: AsyncClient) -> None:
    payload = {
        "name": "Ahmed",
        "email": "ahmed@example.com",
        "phone": "+971551234567",
        "subject": "Need transport",
        "message": "Need quick support for cargo movement",
    }
    create_response = await client.post("/api/v1/public/contact-requests", json=payload)
    assert create_response.status_code == 201

    headers = await _auth_headers(client)
    list_response = await client.get("/api/v1/public/contact-requests", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Ahmed"


@pytest.mark.asyncio
async def test_create_and_list_quote_requests(client: AsyncClient) -> None:
    payload = {
        "name": "Fatima",
        "email": "fatima@example.com",
        "mobile": "+971558887777",
        "freight": "3 Ton",
        "origin": "Dubai",
        "destination": "Abu Dhabi",
        "note": "Urgent requirement",
    }
    create_response = await client.post("/api/v1/public/quote-requests", json=payload)
    assert create_response.status_code == 201

    headers = await _auth_headers(client)
    list_response = await client.get("/api/v1/public/quote-requests", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Fatima"
