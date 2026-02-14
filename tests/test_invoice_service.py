from datetime import date
from decimal import Decimal

from src.models.trip import Trip
from src.services.invoice import InvoiceService


def test_summarize_trips() -> None:
    trip_one = Trip(
        company_id=1,
        date=date(2026, 2, 1),
        freight="1 Ton",
        origin="A",
        destination="B",
        amount=Decimal("100.00"),
        vat=Decimal("5.00"),
        toll_gate=Decimal("10.00"),
        total_amount=Decimal("115.00"),
        driver="D1",
        paid=False,
    )
    trip_two = Trip(
        company_id=1,
        date=date(2026, 2, 2),
        freight="1 Ton",
        origin="A",
        destination="B",
        amount=Decimal("50.00"),
        vat=Decimal("2.50"),
        toll_gate=Decimal("5.00"),
        total_amount=Decimal("57.50"),
        driver="D2",
        paid=False,
    )

    summary = InvoiceService.summarize_trips([trip_one, trip_two])
    assert summary["total_amount"] == Decimal("150.00")
    assert summary["total_vat_amount"] == Decimal("7.50")
    assert summary["total_toll_amount"] == Decimal("15.00")
    assert summary["total_amount_include_vat"] == Decimal("172.50")
