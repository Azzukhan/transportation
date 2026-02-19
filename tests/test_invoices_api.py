import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.models.signatory import Signatory
from src.services.invoice_pdf import InvoicePDFService


async def _auth_headers(
    client: AsyncClient,
    *,
    username: str = "admin",
    password: str = "secret",
) -> dict[str, str]:
    token_response = await client.post(
        "/api/v1/auth/token",
        json={"username": username, "password": password},
    )
    token = token_response.cookies.get("access_token")
    assert token
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_invoice_marks_trips_paid(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    company_payload = {
        "name": "Gamma",
        "address": "Road 2",
        "email": "ops@gamma.example.com",
        "phone": "555",
        "trn": "100000000000003",
        "contact_person": "Kim",
        "po_box": "33",
    }
    company = (await client.post("/api/v1/companies", json=company_payload, headers=headers)).json()

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
    await client.post("/api/v1/trips", json=trip_payload, headers=headers)
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

    trips_response = await client.get(
        "/api/v1/trips", params={"company_id": company["id"]}, headers=headers
    )
    assert trips_response.status_code == 200
    assert trips_response.json()[0]["paid"] is True
    assert trips_response.json()[0]["invoice_id"] == invoice["id"]


@pytest.mark.asyncio
async def test_mark_invoice_paid(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    company_payload = {
        "name": "Delta",
        "address": "Road 4",
        "email": "ops@delta.example.com",
        "phone": "555",
        "trn": "100000000000004",
        "contact_person": "Ana",
        "po_box": "44",
    }
    company = (await client.post("/api/v1/companies", json=company_payload, headers=headers)).json()

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
        headers=headers,
    )
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

    mark_response = await client.patch(
        f"/api/v1/invoices/{invoice_id}/mark-paid", json={}, headers=headers
    )
    assert mark_response.status_code == 200
    assert mark_response.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_download_invoice_pdf_route(
    monkeypatch: pytest.MonkeyPatch, client: AsyncClient, app: FastAPI
) -> None:
    app.state.settings.sensitive_export_step_up_required = False
    headers = await _auth_headers(client)
    company_payload = {
        "name": "Zeta",
        "address": "Road 9",
        "email": "ops@zeta.example.com",
        "phone": "555",
        "trn": "100000000000005",
        "contact_person": "Joe",
        "po_box": "55",
    }
    company = (await client.post("/api/v1/companies", json=company_payload, headers=headers)).json()

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
        headers=headers,
    )
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


@pytest.mark.asyncio
async def test_create_invoice_accepts_custom_invoice_number(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    company = (
        await client.post(
            "/api/v1/companies",
            json={
                "name": "Invoice Custom",
                "address": "Road 8",
                "email": "custom@inv.example.com",
                "phone": "500",
                "trn": "100000000000012",
                "contact_person": "R",
                "po_box": "66",
            },
            headers=headers,
        )
    ).json()

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
        headers=headers,
    )
    response = await client.post(
        "/api/v1/invoices",
        json={
            "company_id": company["id"],
            "start_date": "2026-02-01",
            "end_date": "2026-02-28",
            "invoice_number": "SCT-OLD-14001",
            "prepared_by_mode": "without_signature",
            "format_key": "template_a",
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["invoice_number"] == "SCT-OLD-14001"


@pytest.mark.asyncio
async def test_create_invoice_with_signature_requires_signatory_id(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    company = (
        await client.post(
            "/api/v1/companies",
            json={
                "name": "Signature Co",
                "address": "Road 10",
                "email": "sig@co.example.com",
                "phone": "501",
                "trn": "100000000000013",
                "contact_person": "S",
                "po_box": "67",
            },
            headers=headers,
        )
    ).json()

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
        headers=headers,
    )
    response = await client.post(
        "/api/v1/invoices",
        json={
            "company_id": company["id"],
            "start_date": "2026-02-01",
            "end_date": "2026-02-28",
            "prepared_by_mode": "with_signature",
            "format_key": "template_a",
        },
        headers=headers,
    )
    assert response.status_code == 400
    payload = response.json()
    error_text = payload.get("error", {}).get("message", "")
    assert "signatory_id is required" in error_text


@pytest.mark.asyncio
async def test_signatories_crud_endpoints(client: AsyncClient) -> None:
    headers = await _auth_headers(client)

    created = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Roshan"},
        files={"file": ("signature.png", b"\x89PNG\r\n\x1a\nfake-content", "image/png")},
        headers=headers,
    )
    assert created.status_code == 201
    signatory_id = created.json()["id"]

    listed = await client.get("/api/v1/invoices/signatories", headers=headers)
    assert listed.status_code == 200
    listed_items = listed.json()
    created_item = next(item for item in listed_items if item["id"] == signatory_id)
    assert created_item["has_signature"] is True
    assert "signature_image_data_base64" not in created_item

    signature = await client.get(
        f"/api/v1/invoices/signatories/{signatory_id}/signature", headers=headers
    )
    assert signature.status_code == 200
    assert signature.headers["content-type"] == "image/png"
    assert signature.content.startswith(b"\x89PNG\r\n\x1a\n")

    updated = await client.patch(
        f"/api/v1/invoices/signatories/{signatory_id}",
        data={"name": "Roshan Updated"},
        files={"file": ("signature2.png", b"\x89PNG\r\n\x1a\nupdated-content", "image/png")},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Roshan Updated"

    deleted = await client.delete(f"/api/v1/invoices/signatories/{signatory_id}", headers=headers)
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_signatory_signature_endpoint_requires_auth_and_tenant_access(
    client: AsyncClient,
) -> None:
    owner_headers = await _auth_headers(client, username="admin")
    outsider_headers = await _auth_headers(client, username="admin2")

    created = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Tenant Scoped"},
        files={"file": ("signature.png", b"\x89PNG\r\n\x1a\ntenant-one", "image/png")},
        headers=owner_headers,
    )
    assert created.status_code == 201
    signatory_id = created.json()["id"]

    client.cookies.clear()
    unauth = await client.get(f"/api/v1/invoices/signatories/{signatory_id}/signature")
    assert unauth.status_code == 401

    forbidden_by_tenant = await client.get(
        f"/api/v1/invoices/signatories/{signatory_id}/signature",
        headers=outsider_headers,
    )
    assert forbidden_by_tenant.status_code == 404


@pytest.mark.asyncio
async def test_signatory_signature_endpoint_returns_422_when_decrypt_fails(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    headers = await _auth_headers(client)
    created = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Decrypt Fail"},
        files={"file": ("signature.png", b"\x89PNG\r\n\x1a\nbytes", "image/png")},
        headers=headers,
    )
    assert created.status_code == 201
    signatory_id = created.json()["id"]

    def _raise_decrypt_error(_self: Signatory) -> bytes | None:
        raise ValueError("decrypt failed")

    monkeypatch.setattr(Signatory, "signature_image_data", property(_raise_decrypt_error))

    response = await client.get(f"/api/v1/invoices/signatories/{signatory_id}/signature", headers=headers)
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "signature_decrypt_failed"


@pytest.mark.asyncio
async def test_create_signatory_rejects_invalid_signature_format(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    created = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Bad Format"},
        files={"file": ("signature.txt", b"text", "text/plain")},
        headers=headers,
    )
    assert created.status_code == 400
    assert created.json()["error"]["message"] == "Unsupported signature image format"


@pytest.mark.asyncio
async def test_create_signatory_rejects_duplicate_name(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    first = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Aslam"},
        files={"file": ("signature.png", b"\x89PNG\r\n\x1a\nfirst", "image/png")},
        headers=headers,
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Aslam"},
        files={"file": ("signature2.png", b"\x89PNG\r\n\x1a\nsecond", "image/png")},
        headers=headers,
    )
    assert second.status_code == 400
    assert second.json()["error"]["message"] == "Signatory name already exists"


@pytest.mark.asyncio
async def test_create_signatory_rejects_oversized_image(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    oversized = b"a" * (5 * 1024 * 1024 + 1)
    response = await client.post(
        "/api/v1/invoices/signatories",
        data={"name": "Big Image"},
        files={"file": ("signature.png", oversized, "image/png")},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Signature image must be <= 5MB"


@pytest.mark.asyncio
async def test_update_signatory_returns_404_when_missing(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    response = await client.patch(
        "/api/v1/invoices/signatories/99999",
        data={"name": "Missing"},
        headers=headers,
    )
    assert response.status_code == 404
