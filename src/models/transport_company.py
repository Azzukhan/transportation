from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, BaseModel, IDMixin

if TYPE_CHECKING:
    from src.models.admin_user import AdminUser
    from src.models.company import Company
    from src.models.contact_request import ContactRequest
    from src.models.driver import Driver
    from src.models.driver_cash_handover import DriverCashHandover
    from src.models.employee_salary import EmployeeSalary
    from src.models.invoice import Invoice
    from src.models.quote_request import QuoteRequest
    from src.models.signatory import Signatory
    from src.models.trip import Trip


class TransportCompany(IDMixin, AuditMixin, BaseModel):
    __tablename__ = "transport_companies"

    uuid: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    trn: Mapped[str] = mapped_column(String(30), nullable=False)

    admin_users: Mapped[list[AdminUser]] = relationship(back_populates="transport_company")
    companies: Mapped[list[Company]] = relationship(back_populates="transport_company")
    trips: Mapped[list[Trip]] = relationship(back_populates="transport_company")
    invoices: Mapped[list[Invoice]] = relationship(back_populates="transport_company")
    drivers: Mapped[list[Driver]] = relationship(back_populates="transport_company")
    driver_cash_handovers: Mapped[list[DriverCashHandover]] = relationship(
        back_populates="transport_company"
    )
    employee_salaries: Mapped[list[EmployeeSalary]] = relationship(
        back_populates="transport_company"
    )
    signatories: Mapped[list[Signatory]] = relationship(back_populates="transport_company")
    contact_requests: Mapped[list[ContactRequest]] = relationship(
        back_populates="transport_company"
    )
    quote_requests: Mapped[list[QuoteRequest]] = relationship(back_populates="transport_company")
