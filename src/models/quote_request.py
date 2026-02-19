from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, BaseModel, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.transport_company import TransportCompany


class QuoteRequest(IDMixin, TransportCompanyMixin, AuditMixin, BaseModel):
    __tablename__ = "quote_requests"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    mobile: Mapped[str] = mapped_column(String(40), nullable=False)
    freight: Mapped[str] = mapped_column(String(30), nullable=False)
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new")

    transport_company: Mapped[TransportCompany] = relationship(back_populates="quote_requests")
