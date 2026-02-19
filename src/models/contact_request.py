from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, BaseModel, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.transport_company import TransportCompany


class ContactRequest(IDMixin, TransportCompanyMixin, AuditMixin, BaseModel):
    __tablename__ = "contact_requests"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(40), nullable=False)
    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    source_page: Mapped[str] = mapped_column(String(40), nullable=False, default="contact")

    transport_company: Mapped[TransportCompany] = relationship(back_populates="contact_requests")
