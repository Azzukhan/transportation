from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.driver_cash_handover import DriverCashHandover
    from src.models.transport_company import TransportCompany
    from src.models.trip import Trip


class Driver(IDMixin, TransportCompanyMixin, BaseModel):
    __tablename__ = "drivers"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    mobile_number: Mapped[str] = mapped_column(String(25), nullable=False)
    passport_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    emirates_id_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    emirates_id_expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    trips: Mapped[list[Trip]] = relationship(back_populates="driver_ref")
    cash_handovers: Mapped[list[DriverCashHandover]] = relationship(back_populates="driver")
    transport_company: Mapped[TransportCompany] = relationship(back_populates="drivers")
