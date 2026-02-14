from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.company import Company
from src.models.invoice import Invoice
from src.models.trip import Trip
from src.schemas.invoice import InvoiceCreate
from src.services.invoice import InvoiceService


class InvoiceHandler:
    async def list_invoices(
        self,
        session: AsyncSession,
        company_id: int | None = None,
        status: str | None = None,
    ) -> list[Invoice]:
        stmt: Select[tuple[Invoice]] = select(Invoice)
        if company_id is not None:
            stmt = stmt.where(Invoice.company_id == company_id)

        if status == "paid":
            stmt = stmt.where(Invoice.paid_at.is_not(None))
        elif status == "unpaid":
            stmt = stmt.where(Invoice.paid_at.is_(None))
        elif status == "overdue":
            stmt = stmt.where(Invoice.paid_at.is_(None)).where(Invoice.due_date < date.today())

        stmt = stmt.order_by(Invoice.generated_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_invoice(self, session: AsyncSession, invoice_id: int) -> Invoice:
        invoice = await session.get(Invoice, invoice_id)
        if invoice is None:
            raise AppException("Invoice not found", status_code=404)
        return invoice

    async def get_invoice_bundle(
        self,
        session: AsyncSession,
        invoice_id: int,
    ) -> tuple[Invoice, Company, list[Trip]]:
        invoice = await self.get_invoice(session, invoice_id)
        company = await session.get(Company, invoice.company_id)
        if company is None:
            raise AppException("Company not found", status_code=404)

        stmt: Select[tuple[Trip]] = (
            select(Trip)
            .where(Trip.invoice_id == invoice.id)
            .order_by(Trip.date.asc(), Trip.id.asc())
        )
        trips_result = await session.execute(stmt)
        trips = list(trips_result.scalars().all())

        # Backward compatibility for invoices created before invoice_id linkage.
        if not trips:
            fallback_stmt: Select[tuple[Trip]] = (
                select(Trip)
                .where(Trip.company_id == invoice.company_id)
                .where(Trip.paid.is_(True))
                .where(Trip.date >= invoice.start_date)
                .where(Trip.date <= invoice.end_date)
                .order_by(Trip.date.asc(), Trip.id.asc())
            )
            fallback_result = await session.execute(fallback_stmt)
            trips = list(fallback_result.scalars().all())

        return invoice, company, trips

    async def create_invoice(self, session: AsyncSession, payload: InvoiceCreate) -> Invoice:
        company = await session.get(Company, payload.company_id)
        if company is None:
            raise AppException("Company not found", status_code=404)

        trips = await self._unpaid_trips(
            session=session,
            company_id=payload.company_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
        if not trips:
            raise AppException("No unpaid trips found in selected period", status_code=400)

        summary = InvoiceService.summarize_trips(trips)
        due_date = payload.due_date or payload.end_date + timedelta(days=30)

        invoice = Invoice(
            company_id=payload.company_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            due_date=due_date,
            format_key=payload.format_key,
            total_amount=summary["total_amount_include_vat"],
            generated_at=summary["invoice_date"],
            paid_at=None,
        )

        session.add(invoice)
        await session.flush()

        for trip in trips:
            trip.paid = True
            trip.invoice_id = invoice.id
            company.paid_amount = company.paid_amount + trip.total_amount
            company.unpaid_amount = company.unpaid_amount - trip.total_amount

        await session.commit()
        await session.refresh(invoice)
        return invoice

    async def mark_invoice_paid(
        self,
        session: AsyncSession,
        invoice_id: int,
        paid_at: datetime | None,
    ) -> Invoice:
        invoice = await self.get_invoice(session, invoice_id)
        if invoice.paid_at is not None:
            raise AppException("Invoice is already marked paid", status_code=400)

        invoice.paid_at = paid_at or datetime.now(UTC)
        await session.commit()
        await session.refresh(invoice)
        return invoice

    async def _unpaid_trips(
        self,
        session: AsyncSession,
        company_id: int,
        start_date: date,
        end_date: date,
    ) -> list[Trip]:
        stmt: Select[tuple[Trip]] = (
            select(Trip)
            .where(Trip.company_id == company_id)
            .where(Trip.paid.is_(False))
            .where(Trip.date >= start_date)
            .where(Trip.date <= end_date)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
