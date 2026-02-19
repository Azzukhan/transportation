from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import AppException
from src.models.company import Company
from src.models.invoice import Invoice
from src.models.signatory import Signatory
from src.models.trip import Trip
from src.schemas.invoice import InvoiceCreate
from src.services.invoice import InvoiceService


class InvoiceHandler:
    async def list_invoices(
        self,
        session: AsyncSession,
        transport_company_id: int,
        company_id: int | None = None,
        status: str | None = None,
    ) -> list[Invoice]:
        stmt: Select[tuple[Invoice]] = (
            select(Invoice)
            .options(selectinload(Invoice.signatory))
            .where(Invoice.transport_company_id == transport_company_id)
        )
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

    async def get_invoice(
        self, session: AsyncSession, transport_company_id: int, invoice_id: int
    ) -> Invoice:
        stmt: Select[tuple[Invoice]] = (
            select(Invoice)
            .options(selectinload(Invoice.signatory))
            .where(Invoice.id == invoice_id)
            .where(Invoice.transport_company_id == transport_company_id)
        )
        result = await session.execute(stmt)
        invoice = result.scalar_one_or_none()
        if invoice is None:
            raise AppException("Invoice not found", status_code=404)
        return invoice

    async def get_invoice_bundle(
        self,
        session: AsyncSession,
        transport_company_id: int,
        invoice_id: int,
    ) -> tuple[Invoice, Company, list[Trip]]:
        invoice = await self.get_invoice(session, transport_company_id, invoice_id)
        company = await session.get(Company, invoice.company_id)
        if company is None or company.transport_company_id != transport_company_id:
            raise AppException("Company not found", status_code=404)

        stmt: Select[tuple[Trip]] = (
            select(Trip)
            .where(Trip.invoice_id == invoice.id)
            .where(Trip.transport_company_id == transport_company_id)
            .order_by(Trip.date.asc(), Trip.id.asc())
        )
        trips_result = await session.execute(stmt)
        trips = list(trips_result.scalars().all())

        # Backward compatibility for invoices created before invoice_id linkage.
        if not trips:
            fallback_stmt: Select[tuple[Trip]] = (
                select(Trip)
                .where(Trip.company_id == invoice.company_id)
                .where(Trip.transport_company_id == transport_company_id)
                .where(Trip.paid.is_(True))
                .where(Trip.date >= invoice.start_date)
                .where(Trip.date <= invoice.end_date)
                .order_by(Trip.date.asc(), Trip.id.asc())
            )
            fallback_result = await session.execute(fallback_stmt)
            trips = list(fallback_result.scalars().all())

        return invoice, company, trips

    async def create_invoice(
        self, session: AsyncSession, transport_company_id: int, payload: InvoiceCreate
    ) -> Invoice:
        company = await session.get(Company, payload.company_id)
        if company is None or company.transport_company_id != transport_company_id:
            raise AppException("Company not found", status_code=404)

        if payload.trip_ids:
            trips = await self._specific_unpaid_trips(
                session=session,
                transport_company_id=transport_company_id,
                company_id=payload.company_id,
                trip_ids=payload.trip_ids,
            )
            if not trips:
                raise AppException("No unpaid selected trips found", status_code=400)
            start_date = min(trip.date for trip in trips)
            end_date = max(trip.date for trip in trips)
        else:
            if payload.start_date is None or payload.end_date is None:
                raise AppException(
                    "start_date and end_date are required when trip_ids are not provided",
                    status_code=400,
                )
            start_date = payload.start_date
            end_date = payload.end_date
            trips = await self._unpaid_trips(
                session=session,
                transport_company_id=transport_company_id,
                company_id=payload.company_id,
                start_date=start_date,
                end_date=end_date,
            )
        if not trips:
            raise AppException("No unpaid trips found in selected period", status_code=400)

        summary = InvoiceService.summarize_trips(trips)
        due_date = payload.due_date or end_date + timedelta(days=30)
        prepared_by_mode = payload.prepared_by_mode or "without_signature"
        if prepared_by_mode not in {"without_signature", "with_signature"}:
            raise AppException("Invalid prepared_by_mode", status_code=400)

        selected_signatory: Signatory | None = None
        if prepared_by_mode == "with_signature":
            if payload.signatory_id is None:
                raise AppException(
                    "signatory_id is required when prepared_by_mode is with_signature",
                    status_code=400,
                )
            selected_signatory = await session.get(Signatory, payload.signatory_id)
            if (
                selected_signatory is None
                or selected_signatory.transport_company_id != transport_company_id
            ):
                raise AppException("Selected signatory not found", status_code=404)

        invoice = Invoice(
            company_id=payload.company_id,
            transport_company_id=transport_company_id,
            start_date=start_date,
            end_date=end_date,
            due_date=due_date,
            invoice_number=payload.invoice_number.strip() if payload.invoice_number else None,
            format_key=payload.format_key,
            prepared_by_mode=prepared_by_mode,
            signatory_id=selected_signatory.id if selected_signatory else None,
            signatory_name=selected_signatory.name if selected_signatory else None,
            signatory_image_path=selected_signatory.signature_image_path
            if selected_signatory
            else None,
            signatory_image_mime=selected_signatory.signature_image_mime
            if selected_signatory
            else None,
            signatory_image_data=selected_signatory.signature_image_data
            if selected_signatory
            else None,
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
        transport_company_id: int,
        invoice_id: int,
        paid_at: datetime | None,
    ) -> Invoice:
        invoice = await self.get_invoice(session, transport_company_id, invoice_id)
        if invoice.paid_at is not None:
            raise AppException("Invoice is already marked paid", status_code=400)

        invoice.paid_at = paid_at or datetime.now(UTC)
        await session.commit()
        await session.refresh(invoice)
        return invoice

    async def _unpaid_trips(
        self,
        session: AsyncSession,
        transport_company_id: int,
        company_id: int,
        start_date: date,
        end_date: date,
    ) -> list[Trip]:
        stmt: Select[tuple[Trip]] = (
            select(Trip)
            .where(Trip.company_id == company_id)
            .where(Trip.transport_company_id == transport_company_id)
            .where(Trip.paid.is_(False))
            .where(Trip.date >= start_date)
            .where(Trip.date <= end_date)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def _specific_unpaid_trips(
        self,
        session: AsyncSession,
        transport_company_id: int,
        company_id: int,
        trip_ids: list[int],
    ) -> list[Trip]:
        stmt: Select[tuple[Trip]] = (
            select(Trip)
            .where(Trip.company_id == company_id)
            .where(Trip.transport_company_id == transport_company_id)
            .where(Trip.paid.is_(False))
            .where(Trip.id.in_(trip_ids))
            .order_by(Trip.date.asc(), Trip.id.asc())
        )
        result = await session.execute(stmt)
        trips = list(result.scalars().all())
        found_ids = {trip.id for trip in trips}
        missing_ids = sorted(set(trip_ids) - found_ids)
        if missing_ids:
            raise AppException(
                f"Some selected trips are not available for invoicing: {missing_ids}",
                status_code=400,
            )
        return trips
