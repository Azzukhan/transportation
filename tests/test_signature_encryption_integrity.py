from __future__ import annotations

import json
from base64 import urlsafe_b64decode, urlsafe_b64encode

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.base import Base
from src.models.signatory import Signatory
from src.models.transport_company import TransportCompany
from src.services.signature_encryption_integrity import check_signature_encryption_integrity

_ENVELOPE_PREFIX = b"sigenc:v1:"


def _tamper_encrypted_payload(payload: bytes) -> bytes:
    envelope = json.loads(payload[len(_ENVELOPE_PREFIX) :].decode("utf-8"))
    ciphertext = bytearray(urlsafe_b64decode(envelope["data_ct"].encode("ascii")))
    ciphertext[0] ^= 0x01
    envelope["data_ct"] = urlsafe_b64encode(bytes(ciphertext)).decode("ascii")
    return _ENVELOPE_PREFIX + json.dumps(envelope, separators=(",", ":")).encode("utf-8")


@pytest.mark.asyncio
async def test_integrity_check_reports_invalid_encrypted_rows() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        transport_company = TransportCompany(
            uuid="00000000-0000-0000-0000-000000000055",
            name="Integrity Co",
            email="integrity@co.local",
            location="Integrity City",
            trn="TRN-INTEGRITY-01",
        )
        session.add(transport_company)
        await session.flush()

        signatory = Signatory(
            transport_company_id=transport_company.id,
            name="Tampered Signatory",
            signature_image_mime="image/png",
            signature_image_data=b"valid-signature-bytes",
        )
        session.add(signatory)
        await session.flush()
        assert signatory._signature_image_data is not None
        signatory._signature_image_data = _tamper_encrypted_payload(signatory._signature_image_data)
        await session.commit()

    async with session_factory() as session:
        report = await check_signature_encryption_integrity(session)
        assert report.signatories_checked == 1
        assert report.invalid_signatories == 1
        assert report.invalid_total == 1
        assert report.sample_errors

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()
