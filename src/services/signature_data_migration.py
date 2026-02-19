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
class SignatureRotationReport:
    signatories_reencrypted: int = 0
    invoices_reencrypted: int = 0
    signatories_failed: int = 0
    invoices_failed: int = 0
    failed_signatory_ids: list[int] = field(default_factory=list)
    failed_invoice_ids: list[int] = field(default_factory=list)


async def rotate_signature_blobs(session: AsyncSession) -> SignatureRotationReport:
    crypto = get_signature_crypto()
    report = SignatureRotationReport()

    signatory_stmt: Select[tuple[Signatory]] = select(Signatory).where(
        Signatory._signature_image_data.is_not(None)
    )
    signatory_result = await session.execute(signatory_stmt)
    for signatory in signatory_result.scalars().all():
        try:
            if not crypto.needs_rotation(signatory._signature_image_data):
                continue
            plaintext = signatory.signature_image_data
            signatory.signature_image_data = plaintext
            report.signatories_reencrypted += 1
        except (InvalidTag, ValueError, json.JSONDecodeError, UnicodeDecodeError, TypeError):
            report.signatories_failed += 1
            report.failed_signatory_ids.append(signatory.id)

    invoice_stmt: Select[tuple[Invoice]] = select(Invoice).where(
        Invoice._signatory_image_data.is_not(None)
    )
    invoice_result = await session.execute(invoice_stmt)
    for invoice in invoice_result.scalars().all():
        try:
            if not crypto.needs_rotation(invoice._signatory_image_data):
                continue
            plaintext = invoice.signatory_image_data
            invoice.signatory_image_data = plaintext
            report.invoices_reencrypted += 1
        except (InvalidTag, ValueError, json.JSONDecodeError, UnicodeDecodeError, TypeError):
            report.invoices_failed += 1
            report.failed_invoice_ids.append(invoice.id)

    if report.signatories_reencrypted or report.invoices_reencrypted:
        await session.commit()

    return report
