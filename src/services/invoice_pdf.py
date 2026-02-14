from __future__ import annotations

from io import BytesIO
from typing import Any

from src.core.exceptions import AppException
from src.models.company import Company
from src.models.invoice import Invoice
from src.models.trip import Trip
from src.services.invoice import InvoiceService


class InvoicePDFService:
    @staticmethod
    def _reportlab_modules() -> dict[str, Any]:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.pdfgen import canvas
        except ImportError as exc:
            raise AppException(
                "PDF generation requires reportlab. Install project dependencies and retry.",
                status_code=500,
            ) from exc

        return {
            "A4": A4,
            "mm": mm,
            "canvas": canvas,
        }

    @classmethod
    def generate_pdf(
        cls,
        invoice: Invoice,
        company: Company,
        trips: list[Trip],
        template_key: str | None = None,
    ) -> bytes:
        selected = (template_key or invoice.format_key or "template_a").lower()
        if selected == "standard":
            selected = "template_a"

        if selected == "template_a":
            return cls._template_a(invoice, company, trips)
        if selected == "template_b":
            return cls._template_b(invoice, company, trips)

        raise AppException(f"Unsupported template key: {selected}", status_code=400)

    @classmethod
    def _template_a(cls, invoice: Invoice, company: Company, trips: list[Trip]) -> bytes:
        modules = cls._reportlab_modules()
        page_width, page_height = modules["A4"]
        mm = modules["mm"]
        canvas_cls = modules["canvas"].Canvas

        buffer = BytesIO()
        c = canvas_cls(buffer, pagesize=modules["A4"])

        y = page_height - 20 * mm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(18 * mm, y, company.name)

        c.setFont("Helvetica", 9)
        y -= 5 * mm
        c.drawString(18 * mm, y, f"Tel: {company.phone}")
        y -= 4 * mm
        c.drawString(18 * mm, y, company.address)
        y -= 4 * mm
        c.drawString(18 * mm, y, f"PO Box: {company.po_box}")
        y -= 4 * mm
        c.drawString(18 * mm, y, "TRN: 100390368400003")

        y -= 8 * mm
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(page_width / 2, y, "TAX INVOICE")

        c.setFont("Helvetica", 9)
        y -= 7 * mm
        c.drawString(18 * mm, y, f"Attn: Mr. {company.contact_person}")
        y -= 4 * mm
        c.drawString(18 * mm, y, f"Invoice No: {InvoiceService.generate_invoice_number(invoice.id)}")
        y -= 4 * mm
        c.drawString(18 * mm, y, f"Invoice Date: {invoice.generated_at.date().isoformat()}")
        y -= 4 * mm
        c.drawString(18 * mm, y, f"Due Date: {invoice.due_date.isoformat()}")

        y -= 8 * mm
        headers = [
            "Sr",
            "Date",
            "Description",
            "Amount",
            "VAT",
            "Toll",
            "Total",
            "Remarks",
        ]
        widths = [12, 24, 88, 22, 20, 20, 22, 24]
        x = 14 * mm
        table_height = 7 * mm

        c.setFont("Helvetica-Bold", 8)
        for idx, header in enumerate(headers):
            cell_width = widths[idx] * mm
            c.rect(x, y - table_height, cell_width, table_height, stroke=1, fill=0)
            c.drawCentredString(x + (cell_width / 2), y - 5.2 * mm, header)
            x += cell_width

        y -= table_height
        c.setFont("Helvetica", 8)
        for i, trip in enumerate(trips, start=1):
            row = [
                str(i),
                trip.date.isoformat(),
                f"{trip.origin} to {trip.destination}",
                f"{trip.amount:.2f}",
                f"{trip.vat:.2f}",
                f"{trip.toll_gate:.2f}",
                f"{trip.total_amount:.2f}",
                trip.freight,
            ]

            x = 14 * mm
            for idx, value in enumerate(row):
                cell_width = widths[idx] * mm
                c.rect(x, y - table_height, cell_width, table_height, stroke=1, fill=0)
                if idx == 2:
                    c.drawString(x + 2, y - 5.2 * mm, str(value)[:40])
                else:
                    c.drawCentredString(x + (cell_width / 2), y - 5.2 * mm, str(value))
                x += cell_width

            y -= table_height
            if y < 45 * mm:
                c.showPage()
                y = page_height - 22 * mm

        summary = InvoiceService.summarize_trips(trips)
        y -= 4 * mm
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(page_width - 18 * mm, y, f"Invoice Amount: AED {summary['total_amount']:.2f}")
        y -= 4.5 * mm
        c.drawRightString(page_width - 18 * mm, y, f"VAT Amount 5%: AED {summary['total_vat_amount']:.2f}")
        y -= 4.5 * mm
        c.drawRightString(
            page_width - 18 * mm,
            y,
            f"Total Amount AED: {summary['total_amount_include_vat']:.2f}",
        )

        y -= 12 * mm
        c.setFont("Helvetica", 9)
        c.drawString(24 * mm, y, "Prepared By")
        c.drawCentredString(page_width / 2, y, "Received By")
        c.drawRightString(page_width - 24 * mm, y, "Approved By")

        c.save()
        return buffer.getvalue()

    @classmethod
    def _template_b(cls, invoice: Invoice, company: Company, trips: list[Trip]) -> bytes:
        modules = cls._reportlab_modules()
        page_width, page_height = modules["A4"]
        mm = modules["mm"]
        canvas_cls = modules["canvas"].Canvas

        buffer = BytesIO()
        c = canvas_cls(buffer, pagesize=modules["A4"])

        c.setFillColorRGB(0.05, 0.19, 0.35)
        c.rect(0, page_height - 32 * mm, page_width, 32 * mm, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(16 * mm, page_height - 18 * mm, "INVOICE")
        c.setFont("Helvetica", 10)
        c.drawString(16 * mm, page_height - 24 * mm, company.name)

        c.setFillColorRGB(0.1, 0.1, 0.1)
        y = page_height - 44 * mm
        c.setFont("Helvetica", 9)
        c.drawString(16 * mm, y, f"Invoice No: {InvoiceService.generate_invoice_number(invoice.id)}")
        c.drawRightString(page_width - 16 * mm, y, f"Date: {invoice.generated_at.date().isoformat()}")
        y -= 5 * mm
        c.drawString(16 * mm, y, f"Bill To: {company.contact_person}")
        c.drawRightString(page_width - 16 * mm, y, f"Due: {invoice.due_date.isoformat()}")

        y -= 10 * mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(16 * mm, y, "Route")
        c.drawString(90 * mm, y, "Freight")
        c.drawRightString(page_width - 46 * mm, y, "Date")
        c.drawRightString(page_width - 16 * mm, y, "Total")
        y -= 2 * mm
        c.line(16 * mm, y, page_width - 16 * mm, y)

        c.setFont("Helvetica", 9)
        y -= 6 * mm
        for trip in trips:
            c.drawString(16 * mm, y, f"{trip.origin} -> {trip.destination}")
            c.drawString(90 * mm, y, trip.freight)
            c.drawRightString(page_width - 46 * mm, y, trip.date.isoformat())
            c.drawRightString(page_width - 16 * mm, y, f"AED {trip.total_amount:.2f}")
            y -= 6 * mm
            if y < 45 * mm:
                c.showPage()
                y = page_height - 22 * mm

        summary = InvoiceService.summarize_trips(trips)
        y -= 2 * mm
        c.line(120 * mm, y, page_width - 16 * mm, y)
        y -= 6 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(page_width - 50 * mm, y, "Total")
        c.drawRightString(page_width - 16 * mm, y, f"AED {summary['total_amount_include_vat']:.2f}")

        y -= 10 * mm
        c.setFont("Helvetica", 8)
        c.drawString(16 * mm, y, f"Address: {company.address}")
        y -= 4 * mm
        c.drawString(16 * mm, y, f"Phone: {company.phone} | Email: {company.email}")

        c.save()
        return buffer.getvalue()
