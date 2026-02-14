from fastapi import APIRouter, Query, Response, status

from src.api.deps import CurrentSubjectDep, DBSessionDep
from src.handlers.invoice import InvoiceHandler
from src.schemas.invoice import InvoiceCreate, InvoiceMarkPaid, InvoiceRead
from src.services.invoice_pdf import InvoicePDFService

router = APIRouter(prefix="/invoices", tags=["invoices"])
handler = InvoiceHandler()


@router.get("", response_model=list[InvoiceRead])
async def list_invoices(
    session: DBSessionDep,
    _: CurrentSubjectDep,
    company_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[InvoiceRead]:
    invoices = await handler.list_invoices(session, company_id, status_filter)
    return [InvoiceRead.model_validate(item) for item in invoices]


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    session: DBSessionDep,
    _: CurrentSubjectDep,
) -> InvoiceRead:
    invoice = await handler.create_invoice(session, payload)
    return InvoiceRead.model_validate(invoice)


@router.patch("/{invoice_id}/mark-paid", response_model=InvoiceRead)
async def mark_invoice_paid(
    invoice_id: int,
    payload: InvoiceMarkPaid,
    session: DBSessionDep,
    _: CurrentSubjectDep,
) -> InvoiceRead:
    invoice = await handler.mark_invoice_paid(session, invoice_id, payload.paid_at)
    return InvoiceRead.model_validate(invoice)


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    session: DBSessionDep,
    _: CurrentSubjectDep,
    template_key: str | None = Query(default=None, alias="template"),
) -> Response:
    invoice, company, trips = await handler.get_invoice_bundle(session, invoice_id)
    pdf_bytes = InvoicePDFService.generate_pdf(invoice, company, trips, template_key)
    filename = f"invoice_{invoice_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
