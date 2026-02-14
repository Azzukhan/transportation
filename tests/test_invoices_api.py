import pytest
from httpx import AsyncClient

from src.services.invoice_pdf import InvoicePDFService


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    token_response = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_invoice_marks_trips_paid(client: AsyncClient) -> None:
    company_payload = {
        "name": "Gamma",
        "address": "Road 2",
        "email": "ops@gamma.example.com",
        "phone": "555",
        "contact_person": "Kim",
        "po_box": "33",
    }
    company = (await client.post("/api/v1/companies", json=company_payload)).json()

    trip_payload = {
        "company_id": company["id"],
        "date": "2026-02-05",
        "freight": "3 Ton",
        "origin": "A",
        "destination": "C",
        "amount": "100.00",
        "toll_gate": "5.00",
        "driver": "Driver",
    }
    await client.post("/api/v1/trips", json=trip_payload)

    headers = await _auth_headers(client)
    invoice_payload = {
        "company_id": company["id"],
        "start_date": "2026-02-01",
        "end_date": "2026-02-28",
        "due_date": "2026-03-15",
        "format_key": "template_a",
    }
    invoice_response = await client.post("/api/v1/invoices", json=invoice_payload, headers=headers)
    assert invoice_response.status_code == 201

    invoice = invoice_response.json()
    assert invoice["status"] == "unpaid"

    trips_response = await client.get("/api/v1/trips", params={"company_id": company["id"]})
    assert trips_response.status_code == 200
    assert trips_response.json()[0]["paid"] is True
    assert trips_response.json()[0]["invoice_id"] == invoice["id"]


@pytest.mark.asyncio
async def test_mark_invoice_paid(client: AsyncClient) -> None:
    company_payload = {
        "name": "Delta",
        "address": "Road 4",
        "email": "ops@delta.example.com",
        "phone": "555",
        "contact_person": "Ana",
        "po_box": "44",
    }
    company = (await client.post("/api/v1/companies", json=company_payload)).json()

    await client.post(
        "/api/v1/trips",
        json={
            "company_id": company["id"],
            "date": "2026-02-10",
            "freight": "1 Ton",
            "origin": "X",
            "destination": "Y",
            "amount": "50.00",
            "toll_gate": "5.00",
            "driver": "Driver",
        },
    )

    headers = await _auth_headers(client)
    created = await client.post(
        "/api/v1/invoices",
        json={
            "company_id": company["id"],
            "start_date": "2026-02-01",
            "end_date": "2026-02-28",
            "format_key": "template_a",
        },
        headers=headers,
    )
    invoice_id = created.json()["id"]

    mark_response = await client.patch(f"/api/v1/invoices/{invoice_id}/mark-paid", json={}, headers=headers)
    assert mark_response.status_code == 200
    assert mark_response.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_download_invoice_pdf_route(monkeypatch: pytest.MonkeyPatch, client: AsyncClient) -> None:
    company_payload = {
        "name": "Zeta",
        "address": "Road 9",
        "email": "ops@zeta.example.com",
        "phone": "555",
        "contact_person": "Joe",
        "po_box": "55",
    }
    company = (await client.post("/api/v1/companies", json=company_payload)).json()

    await client.post(
        "/api/v1/trips",
        json={
            "company_id": company["id"],
            "date": "2026-02-10",
            "freight": "1 Ton",
            "origin": "X",
            "destination": "Y",
            "amount": "50.00",
            "toll_gate": "5.00",
            "driver": "Driver",
        },
    )

    headers = await _auth_headers(client)
    created = await client.post(
        "/api/v1/invoices",
        json={
            "company_id": company["id"],
            "start_date": "2026-02-01",
            "end_date": "2026-02-28",
            "format_key": "template_a",
        },
        headers=headers,
    )
    invoice_id = created.json()["id"]

    monkeypatch.setattr(InvoicePDFService, "generate_pdf", lambda *_args, **_kwargs: b"%PDF-FAKE")

    download = await client.get(f"/api/v1/invoices/{invoice_id}/pdf", headers=headers)
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF")
