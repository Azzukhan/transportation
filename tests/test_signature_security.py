from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.signature_crypto import get_signature_crypto
from src.db.base import Base
from src.models.company import Company
from src.models.invoice import Invoice
from src.models.signatory import Signatory
from src.models.transport_company import TransportCompany
from src.services.signature_data_migration import rotate_signature_blobs


def test_signatory_signature_is_encrypted_at_rest() -> None:
    signatory = Signatory(
        transport_company_id=1,
        name="Encrypted",
        signature_image_data=b"\x89PNG\r\n\x1a\nsecure-signature",
        signature_image_mime="image/png",
    )
    assert signatory._signature_image_data is not None
    assert signatory._signature_image_data != b"\x89PNG\r\n\x1a\nsecure-signature"
    assert get_signature_crypto().is_encrypted_payload(signatory._signature_image_data)
    assert signatory.signature_image_data == b"\x89PNG\r\n\x1a\nsecure-signature"


@pytest.mark.asyncio
async def test_rotation_migrates_legacy_plaintext_signature_payloads() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        transport_company = TransportCompany(
            uuid="00000000-0000-0000-0000-000000000099",
            name="Rotate Co",
            email="rotate@co.local",
            location="Rotate City",
            trn="TRN-ROTATE-01",
        )
        session.add(transport_company)
        await session.flush()

        company = Company(
            transport_company_id=transport_company.id,
            name="Rotate Client",
            address="Road",
            email="client@rotate.local",
            phone="000",
            trn="100000000000099",
            contact_person="Rotator",
            po_box="99",
            paid_amount=Decimal("0.00"),
            unpaid_amount=Decimal("0.00"),
        )
        session.add(company)
        await session.flush()

        signatory = Signatory(
            transport_company_id=transport_company.id,
            name="Legacy Sig",
            signature_image_mime="image/png",
        )
        signatory._signature_image_data = b"legacy-signatory-bytes"
        session.add(signatory)
        await session.flush()

        invoice = Invoice(
            company_id=company.id,
            transport_company_id=transport_company.id,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 28),
            due_date=date(2026, 3, 30),
            format_key="standard",
            prepared_by_mode="with_signature",
            signatory_id=signatory.id,
            signatory_name=signatory.name,
            signatory_image_mime="image/png",
            total_amount=Decimal("100.00"),
            generated_at=datetime.now(UTC),
        )
        invoice._signatory_image_data = b"legacy-invoice-bytes"
        session.add(invoice)
        await session.commit()

    async with session_factory() as session:
        report = await rotate_signature_blobs(session)
        assert report.signatories_reencrypted == 1
        assert report.invoices_reencrypted == 1

        refreshed_signatory = await session.get(Signatory, 1)
        assert refreshed_signatory is not None
        assert refreshed_signatory._signature_image_data is not None
        assert refreshed_signatory._signature_image_data != b"legacy-signatory-bytes"
        assert refreshed_signatory.signature_image_data == b"legacy-signatory-bytes"

        refreshed_invoice = await session.get(Invoice, 1)
        assert refreshed_invoice is not None
        assert refreshed_invoice._signatory_image_data is not None
        assert refreshed_invoice._signatory_image_data != b"legacy-invoice-bytes"
        assert refreshed_invoice.signatory_image_data == b"legacy-invoice-bytes"

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_rotation_skips_invalid_encrypted_rows_without_crashing() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        transport_company = TransportCompany(
            uuid="00000000-0000-0000-0000-000000000056",
            name="Broken Co",
            email="broken@co.local",
            location="Broken City",
            trn="TRN-BROKEN-01",
        )
        session.add(transport_company)
        await session.flush()

        signatory = Signatory(
            transport_company_id=transport_company.id,
            name="Broken Sig",
            signature_image_mime="image/png",
        )
        signatory._signature_image_data = b"sigenc:v1:{}"
        session.add(signatory)
        await session.commit()

    async with session_factory() as session:
        report = await rotate_signature_blobs(session)
        assert report.signatories_reencrypted == 0
        assert report.signatories_failed == 1
        assert report.failed_signatory_ids == [1]

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()
