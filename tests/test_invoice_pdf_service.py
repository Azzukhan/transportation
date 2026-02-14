from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from src.core.exceptions import AppException
from src.models.company import Company
from src.models.invoice import Invoice
from src.models.trip import Trip
from src.services.invoice_pdf import InvoicePDFService


class _FakeCanvas:
    def __init__(self, buffer, pagesize):
        self._buffer = buffer
        self._pagesize = pagesize

    def setFont(self, *_args, **_kwargs):
        return None

    def drawString(self, *_args, **_kwargs):
        return None

    def drawCentredString(self, *_args, **_kwargs):
        return None

    def drawRightString(self, *_args, **_kwargs):
        return None

    def rect(self, *_args, **_kwargs):
        return None

    def showPage(self):
        return None

    def setFillColorRGB(self, *_args, **_kwargs):
        return None

    def line(self, *_args, **_kwargs):
        return None

    def save(self):
        self._buffer.write(b"%PDF-FAKE")


@pytest.fixture
def invoice_fixture_data():
    company = Company(
        name="Sikar Cargo",
        address="Dubai",
        email="ops@sikar.example.com",
        phone="+971551234567",
        contact_person="Mohammed",
        po_box="100",
        paid_amount=Decimal("0.00"),
        unpaid_amount=Decimal("0.00"),
    )
    invoice = Invoice(
        id=7,
        company_id=1,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
        due_date=date(2026, 3, 15),
        format_key="template_a",
        notes="",
        total_amount=Decimal("172.50"),
        generated_at=datetime(2026, 2, 28, tzinfo=UTC),
        paid_at=None,
    )
    trips = [
        Trip(
            id=1,
            company_id=1,
            date=date(2026, 2, 1),
            freight="1 Ton",
            origin="Dubai",
            destination="Sharjah",
            amount=Decimal("100.00"),
            vat=Decimal("5.00"),
            toll_gate=Decimal("10.00"),
            total_amount=Decimal("115.00"),
            driver="Driver 1",
            paid=True,
            invoice_id=7,
        ),
        Trip(
            id=2,
            company_id=1,
            date=date(2026, 2, 2),
            freight="3 Ton",
            origin="Ajman",
            destination="Abu Dhabi",
            amount=Decimal("50.00"),
            vat=Decimal("2.50"),
            toll_gate=Decimal("5.00"),
            total_amount=Decimal("57.50"),
            driver="Driver 2",
            paid=True,
            invoice_id=7,
        ),
    ]
    return invoice, company, trips


def test_generate_template_a_pdf(monkeypatch, invoice_fixture_data):
    invoice, company, trips = invoice_fixture_data

    monkeypatch.setattr(
        InvoicePDFService,
        "_reportlab_modules",
        classmethod(lambda cls: {"A4": (595.0, 842.0), "mm": 2.834, "canvas": type("C", (), {"Canvas": _FakeCanvas})}),
    )

    payload = InvoicePDFService.generate_pdf(invoice, company, trips, "template_a")
    assert payload.startswith(b"%PDF")


def test_generate_template_b_pdf(monkeypatch, invoice_fixture_data):
    invoice, company, trips = invoice_fixture_data

    monkeypatch.setattr(
        InvoicePDFService,
        "_reportlab_modules",
        classmethod(lambda cls: {"A4": (595.0, 842.0), "mm": 2.834, "canvas": type("C", (), {"Canvas": _FakeCanvas})}),
    )

    payload = InvoicePDFService.generate_pdf(invoice, company, trips, "template_b")
    assert payload.startswith(b"%PDF")


def test_generate_pdf_rejects_unknown_template(invoice_fixture_data):
    invoice, company, trips = invoice_fixture_data

    with pytest.raises(AppException):
        InvoicePDFService.generate_pdf(invoice, company, trips, "unknown_template")
