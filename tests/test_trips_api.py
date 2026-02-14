import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_trip_updates_totals(client: AsyncClient) -> None:
    company_payload = {
        "name": "Beta",
        "address": "Road 1",
        "email": "ops@beta.example.com",
        "phone": "555",
        "contact_person": "Sam",
        "po_box": "22",
    }
    company = (await client.post("/api/v1/companies", json=company_payload)).json()

    trip_payload = {
        "company_id": company["id"],
        "date": "2026-02-01",
        "freight": "1 Ton",
        "origin": "A",
        "destination": "B",
        "amount": "100.00",
        "toll_gate": "10.00",
        "driver": "Driver",
    }
    trip_response = await client.post("/api/v1/trips", json=trip_payload)
    assert trip_response.status_code == 201
    trip = trip_response.json()
    assert trip["vat"] == "5.00"
    assert trip["total_amount"] == "115.00"
