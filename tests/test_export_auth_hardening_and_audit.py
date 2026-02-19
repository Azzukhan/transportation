from __future__ import annotations

import json
import logging

import pytest
from fastapi import FastAPI
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    token_response = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
    )
    token = token_response.cookies.get("access_token")
    assert token
    return {"Authorization": f"Bearer {token}"}


async def _auth_headers_for(client: AsyncClient, username: str) -> dict[str, str]:
    token_response = await client.post(
        "/api/v1/auth/token",
        json={"username": username, "password": "secret"},
    )
    token = token_response.cookies.get("access_token")
    assert token
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_sensitive_exports_require_step_up_when_enabled(
    client: AsyncClient, app: FastAPI
) -> None:
    settings = app.state.settings
    settings.sensitive_export_step_up_required = True
    settings.sensitive_export_step_up_token = "step-up-test-token"

    headers = await _auth_headers(client)
    company = (
        await client.post(
            "/api/v1/companies",
            json={
                "name": "Step Up Co",
                "address": "Road 1",
                "email": "stepup@example.com",
                "phone": "123",
                "trn": "100000000000901",
                "contact_person": "Owner",
                "po_box": "77",
            },
            headers=headers,
        )
    ).json()
    driver = (
        await client.post(
            "/api/v1/drivers",
            json={"name": "Driver Stepup", "mobile_number": "0500999999"},
            headers=headers,
        )
    ).json()

    await client.post(
        "/api/v1/trips",
        json={
            "company_id": company["id"],
            "date": "2026-02-05",
            "freight": "1 Ton",
            "origin": "A",
            "destination": "B",
            "amount": "100.00",
            "toll_gate": "5.00",
            "driver": driver["name"],
            "driver_id": driver["id"],
        },
        headers=headers,
    )
    invoice = (
        await client.post(
            "/api/v1/invoices",
            json={
                "company_id": company["id"],
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
                "format_key": "standard",
            },
            headers=headers,
        )
    ).json()
    await client.post(
        "/api/v1/employee-salaries",
        json={
            "employee_name": "Stepup Salary",
            "work_permit_no": "12345678",
            "personal_no": "12345678901234",
            "bank_account_no": "A1",
            "fixed_portion": "10.00",
            "variable_portion": "2.00",
        },
        headers=headers,
    )

    invoice_without_stepup = await client.get(
        f"/api/v1/invoices/{invoice['id']}/pdf", headers=headers
    )
    salary_without_stepup = await client.get(
        "/api/v1/employee-salaries/export?month=2&year=2026", headers=headers
    )
    report_without_stepup = await client.get("/api/v1/trips/driver-report/export", headers=headers)
    assert invoice_without_stepup.status_code == 403
    assert salary_without_stepup.status_code == 403
    assert report_without_stepup.status_code == 403
    assert invoice_without_stepup.json()["error"]["code"] == "step_up_required"

    stepup_headers = {**headers, "X-Step-Up-Token": "step-up-test-token"}
    invoice_with_stepup = await client.get(
        f"/api/v1/invoices/{invoice['id']}/pdf", headers=stepup_headers
    )
    salary_with_stepup = await client.get(
        "/api/v1/employee-salaries/export?month=2&year=2026", headers=stepup_headers
    )
    report_with_stepup = await client.get(
        "/api/v1/trips/driver-report/export", headers=stepup_headers
    )
    assert invoice_with_stepup.status_code == 200
    assert salary_with_stepup.status_code == 200
    assert report_with_stepup.status_code == 200


@pytest.mark.asyncio
async def test_driver_report_export_rejects_cross_tenant_driver_id(
    client: AsyncClient, app: FastAPI
) -> None:
    app.state.settings.sensitive_export_step_up_required = False
    admin_one_headers = await _auth_headers_for(client, "admin")
    admin_two_headers = await _auth_headers_for(client, "admin2")

    driver_two = (
        await client.post(
            "/api/v1/drivers",
            json={"name": "Tenant2 Driver", "mobile_number": "0500111222"},
            headers=admin_two_headers,
        )
    ).json()

    response = await client.get(
        "/api/v1/trips/driver-report/export",
        params={"driver_id": driver_two["id"]},
        headers=admin_one_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Driver not found"


@pytest.mark.asyncio
async def test_audit_logs_include_required_fields_and_hash_chain(
    client: AsyncClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="transportation.audit")

    auth_response = await client.post(
        "/api/v1/auth/token",
        json={"username": "admin", "password": "secret"},
        headers={"X-Request-ID": "req-auth-1"},
    )
    assert auth_response.status_code == 200
    token = auth_response.cookies.get("access_token")
    assert token
    headers = {"Authorization": f"Bearer {token}", "X-Request-ID": "req-salary-1"}

    list_response = await client.get("/api/v1/employee-salaries", headers=headers)
    assert list_response.status_code == 200

    audit_records = [r for r in caplog.records if r.name == "transportation.audit"]
    assert len(audit_records) >= 2

    events = [json.loads(record.getMessage()) for record in audit_records[-2:]]
    for event in events:
        assert "actor" in event
        assert "tenant_id" in event
        assert "resource" in event
        assert "action" in event
        assert "timestamp" in event
        assert "request_id" in event
        assert "prev_hash" in event
        assert "event_hash" in event

    assert events[1]["prev_hash"] == events[0]["event_hash"]
