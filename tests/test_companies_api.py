import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_companies(client: AsyncClient) -> None:
    payload = {
        "name": "Acme",
        "address": "Main St",
        "email": "ops@acme.example.com",
        "phone": "123",
        "contact_person": "Alex",
        "po_box": "100",
    }
    create_response = await client.post("/api/v1/companies", json=payload)
    assert create_response.status_code == 201

    list_response = await client.get("/api/v1/companies")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Acme"
