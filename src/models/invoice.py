from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, CompanyMixin, IDMixin

if TYPE_CHECKING:
    from src.models.company import Company


class Invoice(IDMixin, CompanyMixin, BaseModel):
    __tablename__ = "invoices"

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    format_key: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped[Company] = relationship(back_populates="invoices")

    @property
    def status(self) -> str:
        if self.paid_at is not None:
            return "paid"
        if self.due_date < date.today():
            return "overdue"
        return "unpaid"
