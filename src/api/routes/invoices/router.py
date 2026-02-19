import re

from cryptography.exceptions import InvalidTag
from fastapi import APIRouter, File, Form, Query, Request, Response, UploadFile, status
from sqlalchemy import Select, select

from src.api.deps import CurrentAdminDep, DBSessionDep, SettingsDep
from src.core.audit import audit_event, enforce_sensitive_export_step_up
from src.core.exceptions import AppException
from src.core.signature_crypto import get_signature_crypto
from src.handlers.invoice import InvoiceHandler
from src.models.signatory import Signatory
from src.schemas.invoice import (
    InvoiceCreate,
    InvoiceMarkPaid,
    InvoiceRead,
    SignatoryRead,
)
from src.services.invoice_pdf import InvoicePDFService

router = APIRouter(prefix="/invoices", tags=["invoices"])
handler = InvoiceHandler()
ALLOWED_SIGNATURE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/svg+xml",
    "image/webp",
}


async def _read_signature_upload(file: UploadFile) -> tuple[bytes, str]:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_SIGNATURE_MIME_TYPES:
        raise AppException("Unsupported signature image format", status_code=400)

    content = await file.read()
    if not content:
        raise AppException("Empty file upload is not allowed", status_code=400)
    if len(content) > 5 * 1024 * 1024:
        raise AppException("Signature image must be <= 5MB", status_code=400)

    return content, content_type


def _serialize_signatory(signatory: Signatory) -> SignatoryRead:
    return SignatoryRead(
        id=signatory.id,
        name=signatory.name,
        signature_image_mime=signatory.signature_image_mime,
        # Avoid decrypt on list endpoint; this is metadata only.
        has_signature=signatory._signature_image_data is not None,
    )


@router.get("", response_model=list[InvoiceRead])
async def list_invoices(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    company_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[InvoiceRead]:
    invoices = await handler.list_invoices(
        session, current_admin.transport_company_id, company_id, status_filter
    )
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="invoice",
        action="list",
        metadata={"count": len(invoices)},
    )
    return [InvoiceRead.model_validate(item) for item in invoices]


@router.get("/signatories", response_model=list[SignatoryRead])
async def list_signatories(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> list[SignatoryRead]:
    stmt: Select[tuple[Signatory]] = (
        select(Signatory)
        .where(Signatory.transport_company_id == current_admin.transport_company_id)
        .order_by(Signatory.id.asc())
    )
    result = await session.execute(stmt)
    signatories = list(result.scalars().all())
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="signatory",
        action="list",
        metadata={"count": len(signatories)},
    )
    return [_serialize_signatory(item) for item in signatories]


@router.post("/signatories", response_model=SignatoryRead, status_code=status.HTTP_201_CREATED)
async def create_signatory(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    name: str = Form(...),
    file: UploadFile = File(...),
) -> SignatoryRead:
    normalized_name = name.strip()
    if not normalized_name:
        raise AppException("Name is required", status_code=400)

    image_bytes, mime_type = await _read_signature_upload(file)
    existing_stmt: Select[tuple[Signatory]] = (
        select(Signatory)
        .where(Signatory.name == normalized_name)
        .where(Signatory.transport_company_id == current_admin.transport_company_id)
    )
    existing = await session.execute(existing_stmt)
    if existing.scalar_one_or_none() is not None:
        raise AppException("Signatory name already exists", status_code=400)

    signatory = Signatory(
        transport_company_id=current_admin.transport_company_id,
        name=normalized_name,
        signature_image_path=None,
        signature_image_mime=mime_type,
        signature_image_data=image_bytes,
    )
    session.add(signatory)
    await session.commit()
    await session.refresh(signatory)
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="signatory",
        resource_id=str(signatory.id),
        action="create",
    )
    return _serialize_signatory(signatory)


@router.get("/signatories/{signatory_id}/signature")
async def get_signatory_signature(
    request: Request,
    signatory_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> Response:
    stmt: Select[tuple[Signatory]] = (
        select(Signatory)
        .where(Signatory.id == signatory_id)
        .where(Signatory.transport_company_id == current_admin.transport_company_id)
    )
    result = await session.execute(stmt)
    signatory = result.scalar_one_or_none()
    if signatory is None:
        raise AppException("Signatory not found", status_code=404)

    try:
        signature_bytes = signatory.signature_image_data
    except (InvalidTag, ValueError) as exc:
        raise AppException(
            "Signature data cannot be decrypted with current encryption keys. "
            "Restore previous SIGNATURE_ENCRYPTION_KEYS and rotate keys.",
            status_code=422,
            code="signature_decrypt_failed",
        ) from exc
    if not signature_bytes:
        raise AppException("Signature image not found", status_code=404)

    crypto = get_signature_crypto()
    if crypto.needs_rotation(signatory._signature_image_data):
        # Lazy migration: legacy/plaintext or old-key payloads get rewritten with active key.
        signatory.signature_image_data = signature_bytes
        await session.commit()

    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="signatory",
        resource_id=str(signatory.id),
        action="signature_read",
    )
    return Response(
        content=signature_bytes,
        media_type=signatory.signature_image_mime or "application/octet-stream",
        headers={"Cache-Control": "no-store"},
    )


@router.patch("/signatories/{signatory_id}", response_model=SignatoryRead)
async def update_signatory(
    request: Request,
    signatory_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    name: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
) -> SignatoryRead:
    stmt = (
        select(Signatory)
        .where(Signatory.id == signatory_id)
        .where(Signatory.transport_company_id == current_admin.transport_company_id)
    )
    result = await session.execute(stmt)
    signatory = result.scalar_one_or_none()
    if signatory is None:
        raise AppException("Signatory not found", status_code=404)

    if name is not None:
        updated_name = name.strip()
        if not updated_name:
            raise AppException("Name is required", status_code=400)
        existing_stmt: Select[tuple[Signatory]] = (
            select(Signatory)
            .where(Signatory.name == updated_name)
            .where(Signatory.transport_company_id == current_admin.transport_company_id)
            .where(Signatory.id != signatory_id)
        )
        existing = await session.execute(existing_stmt)
        if existing.scalar_one_or_none() is not None:
            raise AppException("Signatory name already exists", status_code=400)
        signatory.name = updated_name

    if file is not None:
        image_bytes, mime_type = await _read_signature_upload(file)
        signatory.signature_image_data = image_bytes
        signatory.signature_image_mime = mime_type
        signatory.signature_image_path = None

    await session.commit()
    await session.refresh(signatory)
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="signatory",
        resource_id=str(signatory.id),
        action="update",
    )
    return _serialize_signatory(signatory)


@router.delete("/signatories/{signatory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_signatory(
    request: Request,
    signatory_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> Response:
    stmt = (
        select(Signatory)
        .where(Signatory.id == signatory_id)
        .where(Signatory.transport_company_id == current_admin.transport_company_id)
    )
    result = await session.execute(stmt)
    signatory = result.scalar_one_or_none()
    if signatory is None:
        raise AppException("Signatory not found", status_code=404)

    await session.delete(signatory)
    await session.commit()
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="signatory",
        resource_id=str(signatory_id),
        action="delete",
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: Request,
    payload: InvoiceCreate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> InvoiceRead:
    invoice = await handler.create_invoice(session, current_admin.transport_company_id, payload)
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="invoice",
        resource_id=str(invoice.id),
        action="create",
    )
    return InvoiceRead.model_validate(invoice)


@router.patch("/{invoice_id}/mark-paid", response_model=InvoiceRead)
async def mark_invoice_paid(
    request: Request,
    invoice_id: int,
    payload: InvoiceMarkPaid,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> InvoiceRead:
    invoice = await handler.mark_invoice_paid(
        session, current_admin.transport_company_id, invoice_id, payload.paid_at
    )
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="invoice",
        resource_id=str(invoice.id),
        action="mark_paid",
    )
    return InvoiceRead.model_validate(invoice)


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    request: Request,
    invoice_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    settings: SettingsDep,
    template_key: str | None = Query(default=None, alias="template"),
) -> Response:
    enforce_sensitive_export_step_up(request, settings)
    invoice, company, trips = await handler.get_invoice_bundle(
        session, current_admin.transport_company_id, invoice_id
    )
    pdf_bytes = InvoicePDFService.generate_pdf(invoice, company, trips, template_key)
    safe_company_name = (
        re.sub(r"[^a-z0-9]+", "-", company.name.lower()).strip("-") or f"company-{company.id}"
    )
    generated_ts = invoice.generated_at.strftime("%Y%m%d_%H%M")
    filename = f"{safe_company_name}_{generated_ts}.pdf"
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="invoice_pdf",
        resource_id=str(invoice.id),
        action="download",
        metadata={"trip_count": len(trips), "template": template_key or "default"},
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
