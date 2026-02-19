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
async def test_create_and_list_driver_cash_handovers_with_filters(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    driver = (
        await client.post(
            "/api/v1/drivers",
            json={
                "name": "Driver Cash A",
                "mobile_number": "0500000001",
            },
            headers=headers,
        )
    ).json()

    create_one = await client.post(
        "/api/v1/driver-cash-handovers",
        json={
            "driver_id": driver["id"],
            "handover_date": "2026-02-12",
            "amount": "100.00",
            "notes": "Fuel advance",
        },
        headers=headers,
    )
    assert create_one.status_code == 201

    create_two = await client.post(
        "/api/v1/driver-cash-handovers",
        json={
            "driver_id": driver["id"],
            "handover_date": "2026-02-15",
            "amount": "200.00",
            "notes": "Food",
        },
        headers=headers,
    )
    assert create_two.status_code == 201

    listed = await client.get(
        "/api/v1/driver-cash-handovers",
        params={"driver_id": driver["id"], "start_date": "2026-02-13", "end_date": "2026-02-28"},
        headers=headers,
    )
    assert listed.status_code == 200
    payload = listed.json()
    assert len(payload) == 1
    assert payload[0]["amount"] == "200.00"
    assert payload[0]["driver_name"] == "Driver Cash A"


@pytest.mark.asyncio
async def test_driver_cash_summary_combines_trips_and_handovers(client: AsyncClient) -> None:
    headers = await _auth_headers(client)

    company = (
        await client.post(
            "/api/v1/companies",
            json={
                "name": "Cash Summary Co",
                "address": "Road 100",
                "email": "cash@summary.example.com",
                "phone": "555",
                "trn": "100000000000222",
                "contact_person": "Owner",
                "po_box": "90",
            },
            headers=headers,
        )
    ).json()

    driver = (
        await client.post(
            "/api/v1/drivers",
            json={
                "name": "Driver Cash B",
                "mobile_number": "0500000002",
            },
            headers=headers,
        )
    ).json()

    for trip_date, amount in [("2026-02-10", "100.00"), ("2026-02-16", "120.00")]:
        created = await client.post(
            "/api/v1/trips",
            json={
                "company_id": company["id"],
                "date": trip_date,
                "freight": "Box",
                "origin": "A",
                "destination": "B",
                "trip_category": "domestic",
                "amount": amount,
                "toll_gate": "0.00",
                "driver": driver["name"],
                "driver_id": driver["id"],
            },
            headers=headers,
        )
        assert created.status_code == 201

    for handover_date, amount in [("2026-02-12", "100.00"), ("2026-02-15", "200.00")]:
        created = await client.post(
            "/api/v1/driver-cash-handovers",
            json={
                "driver_id": driver["id"],
                "handover_date": handover_date,
                "amount": amount,
            },
            headers=headers,
        )
        assert created.status_code == 201

    summary = await client.get(
        "/api/v1/driver-cash-handovers/summary",
        params={"driver_id": driver["id"], "start_date": "2026-02-01", "end_date": "2026-02-28"},
        headers=headers,
    )
    assert summary.status_code == 200
    rows = summary.json()
    assert len(rows) == 1
    row = rows[0]
    assert row["driver_id"] == driver["id"]
    assert row["trip_count"] == 2
    assert row["earned_amount_total"] == "220.00"
    assert row["handover_amount_total"] == "300.00"
    assert row["balance_amount"] == "-80.00"
