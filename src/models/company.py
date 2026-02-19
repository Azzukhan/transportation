from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.invoice import Invoice
    from src.models.transport_company import TransportCompany
    from src.models.trip import Trip


class Company(IDMixin, TransportCompanyMixin, BaseModel):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    trn: Mapped[str] = mapped_column(String(30), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(25), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    unpaid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    po_box: Mapped[str] = mapped_column(String(20), nullable=False)

    trips: Mapped[list[Trip]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    invoices: Mapped[list[Invoice]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    transport_company: Mapped[TransportCompany] = relationship(back_populates="companies")
