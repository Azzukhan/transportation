from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import LargeBinary, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.signature_crypto import get_signature_crypto
from src.models.base import BaseModel, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.invoice import Invoice
    from src.models.transport_company import TransportCompany


class Signatory(IDMixin, TransportCompanyMixin, BaseModel):
    __tablename__ = "signatories"
    __table_args__ = (
        UniqueConstraint(
            "transport_company_id", "name", name="uq_signatories_transport_company_id_name"
        ),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    signature_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signature_image_mime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    _signature_image_data: Mapped[bytes | None] = mapped_column(
        "signature_image_data", LargeBinary, nullable=True
    )

    invoices: Mapped[list[Invoice]] = relationship(back_populates="signatory")
    transport_company: Mapped[TransportCompany] = relationship(back_populates="signatories")

    @property
    def signature_image_data(self) -> bytes | None:
        decrypted = get_signature_crypto().decrypt_payload(self._signature_image_data)
        return decrypted.data if decrypted is not None else None

    @signature_image_data.setter
    def signature_image_data(self, value: bytes | None) -> None:
        self._signature_image_data = get_signature_crypto().encrypt_for_storage(value)
