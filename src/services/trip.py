from decimal import Decimal

from src.models.trip import Trip


class TripService:
    VAT_RATE = Decimal("0.05")

    @classmethod
    def calculate_amounts(
        cls, amount: Decimal, toll_gate: Decimal, trip_category: str = "domestic"
    ) -> tuple[Decimal, Decimal]:
        vat = Decimal("0.00") if trip_category == "international" else amount * cls.VAT_RATE
        total = amount + vat + toll_gate
        return vat, total

    @classmethod
    def apply_trip_amounts(cls, trip: Trip) -> None:
        trip.vat, trip.total_amount = cls.calculate_amounts(
            trip.amount, trip.toll_gate, trip.trip_category
        )
