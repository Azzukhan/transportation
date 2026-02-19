from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, LargeBinary, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.signature_crypto import get_signature_crypto
from src.models.base import BaseModel, CompanyMixin, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.signatory import Signatory
    from src.models.transport_company import TransportCompany


class Invoice(IDMixin, CompanyMixin, TransportCompanyMixin, BaseModel):
    __tablename__ = "invoices"

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    invoice_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    format_key: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    prepared_by_mode: Mapped[str] = mapped_column(
        String(25), nullable=False, default="without_signature"
    )
    signatory_id: Mapped[int | None] = mapped_column(
        ForeignKey("signatories.id", ondelete="SET NULL"),
        nullable=True,
    )
    signatory_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    signatory_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signatory_image_mime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    _signatory_image_data: Mapped[bytes | None] = mapped_column(
        "signatory_image_data", LargeBinary, nullable=True
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped[Company] = relationship(back_populates="invoices")
    signatory: Mapped[Signatory | None] = relationship(back_populates="invoices")
    transport_company: Mapped[TransportCompany] = relationship(back_populates="invoices")

    @property
    def status(self) -> str:
        if self.paid_at is not None:
            return "paid"
        if self.due_date < date.today():
            return "overdue"
        return "unpaid"

    @property
    def signatory_image_data(self) -> bytes | None:
        decrypted = get_signature_crypto().decrypt_payload(self._signatory_image_data)
        return decrypted.data if decrypted is not None else None

    @signatory_image_data.setter
    def signatory_image_data(self, value: bytes | None) -> None:
        self._signatory_image_data = get_signature_crypto().encrypt_for_storage(value)
