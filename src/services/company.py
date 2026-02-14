from decimal import Decimal

from src.models.company import Company


class CompanyService:
    @staticmethod
    def apply_unpaid_delta(company: Company, delta: Decimal) -> None:
        company.unpaid_amount = company.unpaid_amount + delta

    @staticmethod
    def apply_paid_delta(company: Company, delta: Decimal) -> None:
        company.paid_amount = company.paid_amount + delta
