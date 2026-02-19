from __future__ import annotations

import json
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidTag
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.signature_crypto import get_signature_crypto
from src.models.invoice import Invoice
from src.models.signatory import Signatory


@dataclass(slots=True)
class SignatureIntegrityReport:
    signatories_checked: int = 0
    invoices_checked: int = 0
    invalid_signatories: int = 0
    invalid_invoices: int = 0
    sample_errors: list[str] = field(default_factory=list)

    @property
    def checked_total(self) -> int:
        return self.signatories_checked + self.invoices_checked

    @property
    def invalid_total(self) -> int:
        return self.invalid_signatories + self.invalid_invoices


def _append_sample(report: SignatureIntegrityReport, message: str, limit: int) -> None:
    if len(report.sample_errors) < limit:
        report.sample_errors.append(message)


async def check_signature_encryption_integrity(
    session: AsyncSession,
    *,
    sample_limit: int = 10,
) -> SignatureIntegrityReport:
    crypto = get_signature_crypto()
    report = SignatureIntegrityReport()

    signatory_stmt: Select[tuple[int, bytes | None]] = select(
        Signatory.id, Signatory._signature_image_data
    ).where(Signatory._signature_image_data.is_not(None))
    signatory_rows = await session.execute(signatory_stmt)
    for signatory_id, raw_payload in signatory_rows.all():
        if raw_payload is None:
            continue
        report.signatories_checked += 1
        try:
            crypto.decrypt_payload(raw_payload)
        except (InvalidTag, ValueError, json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            report.invalid_signatories += 1
            _append_sample(
                report,
                f"signatory:{signatory_id} {type(exc).__name__}",
                sample_limit,
            )

    invoice_stmt: Select[tuple[int, bytes | None]] = select(
        Invoice.id, Invoice._signatory_image_data
    ).where(Invoice._signatory_image_data.is_not(None))
    invoice_rows = await session.execute(invoice_stmt)
    for invoice_id, raw_payload in invoice_rows.all():
        if raw_payload is None:
            continue
        report.invoices_checked += 1
        try:
            crypto.decrypt_payload(raw_payload)
        except (InvalidTag, ValueError, json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            report.invalid_invoices += 1
            _append_sample(
                report,
                f"invoice:{invoice_id} {type(exc).__name__}",
                sample_limit,
            )

    return report
