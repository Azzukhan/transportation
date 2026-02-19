from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, BaseModel, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.driver import Driver
    from src.models.transport_company import TransportCompany


class DriverCashHandover(IDMixin, TransportCompanyMixin, AuditMixin, BaseModel):
    __tablename__ = "driver_cash_handovers"

    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    handover_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    driver: Mapped[Driver] = relationship(back_populates="cash_handovers")
    transport_company: Mapped[TransportCompany] = relationship(
        back_populates="driver_cash_handovers"
    )
