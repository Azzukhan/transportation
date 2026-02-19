import pytest
from httpx import AsyncClient


def _tenant_headers(uuid: str = "00000000-0000-0000-0000-000000000001") -> dict[str, str]:
    return {"X-Transport-Company-UUID": uuid}


async def _auth_headers(client: AsyncClient, username: str = "admin") -> dict[str, str]:
    token_response = await client.post(
        "/api/v1/auth/token",
        json={"username": username, "password": "secret"},
    )
    token = token_response.cookies.get("access_token")
    assert token
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
    create_response = await client.post(
        "/api/v1/public/contact-requests", json=payload, headers=_tenant_headers()
    )
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
    create_response = await client.post(
        "/api/v1/public/quote-requests", json=payload, headers=_tenant_headers()
    )
    assert create_response.status_code == 201

    headers = await _auth_headers(client)
    list_response = await client.get("/api/v1/public/quote-requests", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Fatima"


@pytest.mark.asyncio
async def test_public_request_requires_explicit_tenant(client: AsyncClient) -> None:
    payload = {
        "name": "No Tenant",
        "email": "tenantless@example.com",
        "phone": "+971551230000",
        "subject": "Missing tenant",
        "message": "No tenant headers provided",
    }
    response = await client.post("/api/v1/public/contact-requests", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "tenant_unresolved"


@pytest.mark.asyncio
async def test_public_request_isolation_across_tenants(client: AsyncClient) -> None:
    payload = {
        "name": "Tenant Two Lead",
        "email": "tenant2@example.com",
        "phone": "+971551239999",
        "subject": "Tenant 2 inquiry",
        "message": "Scoped to second tenant",
    }
    created = await client.post(
        "/api/v1/public/contact-requests",
        json=payload,
        headers=_tenant_headers("00000000-0000-0000-0000-000000000002"),
    )
    assert created.status_code == 201

    admin_one_headers = await _auth_headers(client, "admin")
    admin_two_headers = await _auth_headers(client, "admin2")

    listed_for_admin_one = await client.get(
        "/api/v1/public/contact-requests", headers=admin_one_headers
    )
    assert listed_for_admin_one.status_code == 200
    assert all(item["name"] != "Tenant Two Lead" for item in listed_for_admin_one.json())

    listed_for_admin_two = await client.get(
        "/api/v1/public/contact-requests", headers=admin_two_headers
    )
    assert listed_for_admin_two.status_code == 200
    assert any(item["name"] == "Tenant Two Lead" for item in listed_for_admin_two.json())
