from datetime import UTC, datetime
from decimal import Decimal

from src.models.trip import Trip


class InvoiceService:
    @staticmethod
    def generate_invoice_number(invoice_id: int) -> str:
        return f"TAX/IN/{invoice_id}"

    @staticmethod
    def summarize_trips(trips: list[Trip]) -> dict[str, Decimal | datetime]:
        total_amount = sum((trip.amount for trip in trips), Decimal("0.00"))
        total_vat_amount = sum((trip.vat for trip in trips), Decimal("0.00"))
        total_toll_amount = sum((trip.toll_gate for trip in trips), Decimal("0.00"))
        total_amount_include_vat = sum((trip.total_amount for trip in trips), Decimal("0.00"))
        return {
            "total_amount": total_amount,
            "total_vat_amount": total_vat_amount,
            "total_toll_amount": total_toll_amount,
            "total_amount_include_vat": total_amount_include_vat,
            "invoice_date": datetime.now(UTC),
        }
