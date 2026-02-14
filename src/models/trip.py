from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, CompanyMixin, IDMixin

if TYPE_CHECKING:
    from src.models.company import Company


class Trip(IDMixin, CompanyMixin, BaseModel):
    __tablename__ = "trips"

    date: Mapped[date] = mapped_column(Date, nullable=False)
    freight: Mapped[str] = mapped_column(String(25), nullable=False)
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    vat: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    toll_gate: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    driver: Mapped[str] = mapped_column(String(30), nullable=False)
    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id", ondelete="SET NULL"),
        nullable=True,
    )

    company: Mapped[Company] = relationship(back_populates="trips")
