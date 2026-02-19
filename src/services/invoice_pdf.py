from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, cast

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
        if selected in {"template_c", "detailed"}:
            return cls._template_c(invoice, company, trips)

        raise AppException(f"Unsupported template key: {selected}", status_code=400)

    @classmethod
    def _draw_brand_header(
        cls,
        c: Any,
        page_width: float,
        y_top: float,
    ) -> float:
        """
        Draws a centered branded SVG header.
        Returns the y-coordinate below the header block.
        """
        modules = cls._reportlab_modules()
        mm = modules["mm"]

        def _draw_text_fallback() -> float:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(18 * mm, y_top, "سيكار لنقل المواد العامة")
            c.drawString(18 * mm, y_top - (5 * mm), "بالشاحنات الثقيلة والخفيفة ذ.م.م")
            c.setFont("Helvetica-Bold", 14)
            c.drawRightString(page_width - 18 * mm, y_top, "Sikar Cargo Transport")
            c.drawRightString(
                page_width - 18 * mm, y_top - (5 * mm), "By Heavy & Light Trucks L.L.C"
            )
            c.line(18 * mm, y_top - (7 * mm), page_width - 18 * mm, y_top - (7 * mm))
            return cast(float, y_top - (12 * mm))

        root = Path(__file__).resolve().parents[2]
        candidates = [
            root / "frontend" / "public" / "Sikar_cargo_transport_logo.png",
            root / "frontend" / "public" / "sikar_invoice_header_A4_exactstyle.svg",
            root / "frontend" / "public" / "sikar_invoice_header.svg",
            root / "frontend" / "public" / "sikar transport logo.svg",
        ]

        header_asset = next((path for path in candidates if path.exists()), None)
        if header_asset is None:
            return _draw_text_fallback()

        target_width = page_width - (24 * mm)

        # If a pre-designed bitmap header is available, render it directly.
        if header_asset.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            try:
                from reportlab.lib.utils import ImageReader

                image = ImageReader(str(header_asset))
                image_width, image_height = image.getSize()
                if image_width > 0 and image_height > 0:
                    draw_height = target_width * (image_height / image_width)
                    x = (page_width - target_width) / 2
                    y = y_top - draw_height
                    c.drawImage(
                        image,
                        x,
                        y,
                        width=target_width,
                        height=draw_height,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
                    return cast(float, y - (4 * mm))
            except Exception:
                pass

        # Preferred path: rasterize SVG first so Arabic glyph shaping/rendering
        # is preserved consistently in generated PDFs.
        try:
            import cairosvg
            from reportlab.lib.utils import ImageReader

            png_bytes = cairosvg.svg2png(
                url=str(header_asset),
                output_width=max(1, int(target_width * 2.8)),
            )
            image = ImageReader(BytesIO(png_bytes))
            image_width, image_height = image.getSize()
            if image_width > 0 and image_height > 0:
                draw_height = target_width * (image_height / image_width)
                x = (page_width - target_width) / 2
                y = y_top - draw_height
                c.drawImage(
                    image,
                    x,
                    y,
                    width=target_width,
                    height=draw_height,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                return cast(float, y - (4 * mm))
        except Exception:
            # Fall back to vector rendering below.
            pass

        try:
            from reportlab.graphics import renderPDF
            from svglib.svglib import svg2rlg
        except ImportError:
            return _draw_text_fallback()

        drawing = svg2rlg(str(header_asset))
        if drawing is None:
            return _draw_text_fallback()

        scale = target_width / drawing.width if drawing.width else 1.0
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)

        x = (page_width - drawing.width) / 2
        y = y_top - drawing.height
        renderPDF.draw(drawing, c, x, y)
        return cast(float, y - (4 * mm))

    @classmethod
    def _template_a(cls, invoice: Invoice, company: Company, trips: list[Trip]) -> bytes:
        modules = cls._reportlab_modules()
        page_width, page_height = modules["A4"]
        mm = modules["mm"]
        canvas_cls = modules["canvas"].Canvas

        buffer = BytesIO()
        c = canvas_cls(buffer, pagesize=modules["A4"])

        y = page_height - 14 * mm
        y = cls._draw_brand_header(c, page_width, y)

        invoice_no = InvoiceService.generate_invoice_number(invoice.id, invoice.invoice_number)
        invoice_date = invoice.generated_at.date().strftime("%d-%b-%Y")

        # Block 1 (below header with margin): customer details on left.
        y -= 3 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(14 * mm, y, f"Ms/ {company.name}")
        c.setFont("Helvetica-Bold", 8)
        y -= 4.1 * mm
        c.drawString(14 * mm, y, f"TRN:- {company.trn or '-'}")
        y -= 4.1 * mm
        c.drawString(14 * mm, y, f"Mobile Number:- {company.phone or '-'}")

        # Block 2 (separate row): centered TAX INVOICE + TRN.
        y -= 6 * mm
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(page_width / 2, y, "TAX INVOICE")
        y -= 4.6 * mm
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(page_width / 2, y, f"TRN:- {company.trn or '-'}")

        # Block 3 (separate row): invoice metadata on left.
        y -= 8 * mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(14 * mm, y, f"Invoice No. :- {invoice_no}")
        y -= 4.1 * mm
        c.drawString(14 * mm, y, f"Invoice Date :- {invoice_date}")

        y -= 6 * mm
        headers = [
            ["Sr No."],
            ["Delivery", "Date"],
            ["Description"],
            ["Amount", "(Excl. VAT)"],
            ["VAT 5%"],
            ["Pass &", "Parking"],
            ["Total", "Amount"],
            ["Remarks"],
        ]
        # Total width: 182mm (fits A4 printable area from 14mm to 196mm).
        widths = [10, 22, 56, 18, 14, 14, 20, 28]
        x = 14 * mm
        header_height = 13 * mm
        row_height = 7.5 * mm

        c.setFont("Helvetica-Bold", 6.6)
        for idx, header_lines in enumerate(headers):
            cell_width = widths[idx] * mm
            c.rect(x, y - header_height, cell_width, header_height, stroke=1, fill=0)
            if len(header_lines) == 1:
                c.drawCentredString(x + (cell_width / 2), y - 8.0 * mm, header_lines[0])
            else:
                c.drawCentredString(x + (cell_width / 2), y - 5.6 * mm, header_lines[0])
                c.drawCentredString(x + (cell_width / 2), y - 9.8 * mm, header_lines[1])
            x += cell_width

        y -= header_height
        c.setFont("Helvetica", 7)
        for i, trip in enumerate(trips, start=1):
            destination_company = (trip.destination_company_name or "").strip() or "Destination N/A"
            row = [
                str(i),
                trip.date.strftime("%d-%b-%Y"),
                f"{trip.origin} to {destination_company} ({trip.destination})",
                f"{trip.amount:.2f}",
                f"{trip.vat:.2f}",
                f"{trip.toll_gate:.2f}",
                f"{trip.total_amount:.2f}",
                trip.freight,
            ]

            x = 14 * mm
            for idx, value in enumerate(row):
                cell_width = widths[idx] * mm
                c.rect(x, y - row_height, cell_width, row_height, stroke=1, fill=0)
                if idx == 2:
                    c.drawString(x + 1.5 * mm, y - 5.2 * mm, str(value)[:40])
                else:
                    c.drawCentredString(x + (cell_width / 2), y - 5.2 * mm, str(value))
                x += cell_width

            y -= row_height
            if y < 55 * mm:
                c.showPage()
                y = page_height - 22 * mm

        summary = InvoiceService.summarize_trips(trips)
        total_toll = summary.get("total_toll_amount", summary.get("total_toll_gate", 0))
        total_row = [
            "",
            "",
            "",
            f"{summary['total_amount']:.2f}",
            f"{summary['total_vat_amount']:.2f}",
            f"{total_toll:.2f}",
            f"{summary['total_amount_include_vat']:.2f}",
            "",
        ]
        x = 14 * mm
        c.setFont("Helvetica-Bold", 8)
        for idx, value in enumerate(total_row):
            cell_width = widths[idx] * mm
            c.rect(x, y - row_height, cell_width, row_height, stroke=1, fill=0)
            c.drawCentredString(x + (cell_width / 2), y - 5.1 * mm, value)
            x += cell_width
        y -= row_height

        y -= 9 * mm
        c.setFont("Helvetica", 9)
        c.drawString(14 * mm, y, "Prepare By  :-")
        c.drawCentredString(page_width / 2, y, "Recived By")
        c.drawRightString(page_width - 14 * mm, y, "Approved By :-")

        if invoice.prepared_by_mode == "with_signature":
            # Larger signature, placed right under "Prepare By :-"
            cls._draw_prepare_by_signature(c, invoice, 16 * mm, y + (0.8 * mm), 46 * mm, 20 * mm)

        # Footer block (fixed near page bottom) matching reference invoice style.
        footer_line_y = 14 * mm
        c.setLineWidth(1)
        c.line(14 * mm, footer_line_y, page_width - 14 * mm, footer_line_y)
        c.setFont("Helvetica", 8.5)
        c.drawCentredString(
            page_width / 2,
            footer_line_y - (4.5 * mm),
            "P.O. Box : 20124, Phone: 971 4 2503886, Fax: 971 4 2516492, Mobile: 971 55 2381722",
        )
        c.drawCentredString(
            page_width / 2, footer_line_y - (8.5 * mm), "E-mail : sikarcargo@gmail.com"
        )

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
        c.drawString(
            16 * mm,
            y,
            f"Invoice No: {InvoiceService.generate_invoice_number(invoice.id, invoice.invoice_number)}",
        )
        c.drawRightString(
            page_width - 16 * mm, y, f"Date: {invoice.generated_at.date().isoformat()}"
        )
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

    @classmethod
    def _template_c(cls, invoice: Invoice, company: Company, trips: list[Trip]) -> bytes:
        modules = cls._reportlab_modules()
        page_width, page_height = modules["A4"]
        mm = modules["mm"]
        canvas_cls = modules["canvas"].Canvas

        buffer = BytesIO()
        c = canvas_cls(buffer, pagesize=modules["A4"])

        invoice_no = InvoiceService.generate_invoice_number(invoice.id, invoice.invoice_number)
        invoice_date = invoice.generated_at.date().strftime("%d-%b-%Y")
        invoice_month = invoice.generated_at.strftime("%b-%y")

        headers = [
            ["Sr No."],
            ["Delivery", "Date"],
            ["Description"],
            ["Amount", "(Excl. VAT)"],
            ["VAT%"],
            ["VAT"],
            ["Total", "Amount"],
            ["Remarks"],
        ]
        widths = [10, 20, 62, 18, 12, 12, 20, 28]
        header_height = 12.5 * mm
        row_height = 7.2 * mm
        table_x = 14 * mm

        def draw_page_header(first_page: bool) -> float:
            y_top = page_height - 14 * mm
            y = cls._draw_brand_header(c, page_width, y_top)

            if first_page:
                # Match template_a header/info alignment.
                y -= 3 * mm
                c.setFont("Helvetica-Bold", 10)
                c.drawString(14 * mm, y, f"Ms/ {company.name}")
                c.setFont("Helvetica-Bold", 8)
                y -= 4.1 * mm
                c.drawString(14 * mm, y, f"TRN:- {company.trn or '-'}")
                y -= 4.1 * mm
                c.drawString(14 * mm, y, f"Mobile Number:- {company.phone or '-'}")

                y -= 6 * mm
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(page_width / 2, y, "TAX INVOICE")

                y -= 4.6 * mm
                c.setFont("Helvetica-Bold", 9)
                c.drawCentredString(page_width / 2, y, invoice_month)

                y -= 8 * mm
                c.drawString(14 * mm, y, f"Invoice No. :- {invoice_no}")
                y -= 4.1 * mm
                c.drawString(14 * mm, y, f"Invoice Date :- {invoice_date}")
                y -= 4.1 * mm
                c.drawString(14 * mm, y, f"TRN:- {company.trn or '-'}")
            else:
                y -= 2.5 * mm
                c.setFont("Helvetica-Bold", 9)
                c.drawString(14 * mm, y, f"Invoice No. :- {invoice_no}")
                y -= 4.6 * mm
                c.setFont("Helvetica-Bold", 8)
                c.drawString(14 * mm, y, f"Invoice Date :- {invoice_date}")
                y -= 4.2 * mm
                c.setFont("Helvetica", 7.2)
                c.drawString(14 * mm, y, "Continued trip details")

            y -= 6 * mm
            x = table_x
            c.setFont("Helvetica-Bold", 6.5)
            for idx, header_lines in enumerate(headers):
                cell_width = widths[idx] * mm
                c.rect(x, y - header_height, cell_width, header_height, stroke=1, fill=0)
                if len(header_lines) == 1:
                    c.drawCentredString(x + (cell_width / 2), y - 7.7 * mm, header_lines[0])
                else:
                    c.drawCentredString(x + (cell_width / 2), y - 5.3 * mm, header_lines[0])
                    c.drawCentredString(x + (cell_width / 2), y - 9.4 * mm, header_lines[1])
                x += cell_width
            return cast(float, y - header_height)

        def draw_footer() -> None:
            footer_line_y = 14 * mm
            c.setLineWidth(1)
            c.line(14 * mm, footer_line_y, page_width - 14 * mm, footer_line_y)
            c.setFont("Helvetica", 8.2)
            c.drawCentredString(
                page_width / 2,
                footer_line_y - (4.5 * mm),
                "P.O. Box : 20124, Phone: 971 4 2503886, Fax: 971 4 2516492, Mobile: 971 55 2381722",
            )
            c.drawCentredString(
                page_width / 2, footer_line_y - (8.5 * mm), "E-mail : sikarcargo@gmail.com"
            )

        y = draw_page_header(first_page=True)
        c.setFont("Helvetica", 7)

        for i, trip in enumerate(trips, start=1):
            # Keep enough space for next row and footer; otherwise continue on next page.
            if y - row_height < 34 * mm:
                draw_footer()
                c.showPage()
                y = draw_page_header(first_page=False)
                c.setFont("Helvetica", 7)

            destination_company = (trip.destination_company_name or "").strip() or "Destination N/A"
            row = [
                str(i),
                trip.date.strftime("%d-%b-%Y"),
                f"{destination_company} ({trip.destination})",
                f"{trip.amount:.2f}",
                "0%" if float(trip.vat) == 0 else "5%",
                f"{trip.vat:.2f}",
                f"{trip.total_amount:.2f}",
                trip.freight,
            ]

            x = table_x
            for idx, value in enumerate(row):
                cell_width = widths[idx] * mm
                c.rect(x, y - row_height, cell_width, row_height, stroke=1, fill=0)
                if idx == 2:
                    c.drawString(x + 1.4 * mm, y - 5.0 * mm, str(value)[:52])
                else:
                    c.drawCentredString(x + (cell_width / 2), y - 5.0 * mm, str(value))
                x += cell_width
            y -= row_height

        summary = InvoiceService.summarize_trips(trips)

        if y - (row_height + (28 * mm)) < 24 * mm:
            draw_footer()
            c.showPage()
            y = draw_page_header(first_page=False)

        total_row = [
            "",
            "",
            "",
            f"{summary['total_amount']:.2f}",
            "",
            f"{summary['total_vat_amount']:.2f}",
            f"{summary['total_amount_include_vat']:.2f}",
            "",
        ]
        x = table_x
        c.setFont("Helvetica-Bold", 7.8)
        for idx, value in enumerate(total_row):
            cell_width = widths[idx] * mm
            c.rect(x, y - row_height, cell_width, row_height, stroke=1, fill=0)
            c.drawCentredString(x + (cell_width / 2), y - 5.0 * mm, value)
            x += cell_width
        y -= row_height

        y -= 9 * mm
        c.setFont("Helvetica", 9)
        c.drawString(14 * mm, y, "Prepare By  :-")
        c.drawCentredString(page_width / 2, y, "Recived By")
        c.drawRightString(page_width - 14 * mm, y, "Approved By :-")

        if invoice.prepared_by_mode == "with_signature":
            cls._draw_prepare_by_signature(c, invoice, 16 * mm, y + (0.8 * mm), 46 * mm, 20 * mm)

        draw_footer()
        c.save()
        return buffer.getvalue()

    @classmethod
    def _draw_prepare_by_signature(
        cls,
        c: Any,
        invoice: Invoice,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        if cls._draw_signature_image_from_bytes(
            c=c,
            image_bytes=invoice.signatory_image_data,
            image_mime=invoice.signatory_image_mime,
            x=x,
            y=y,
            width=width,
            height=height,
        ):
            return

        image_path = cls._resolve_public_asset_path(invoice.signatory_image_path)
        if image_path is not None:
            cls._draw_signature_image_from_path(
                c=c,
                image_path=image_path,
                x=x,
                y=y,
                width=width,
                height=height,
            )

    @staticmethod
    def _draw_signature(
        c: Any,
        image: Any,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        c.drawImage(
            image,
            x,
            y - height,
            width=width,
            height=height,
            preserveAspectRatio=True,
            anchor="sw",
            mask="auto",
        )

    @classmethod
    def _draw_signature_image_from_bytes(
        cls,
        c: Any,
        image_bytes: bytes | None,
        image_mime: str | None,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> bool:
        if not image_bytes:
            return False

        is_svg = (image_mime or "").lower() == "image/svg+xml"
        try:
            from reportlab.lib.utils import ImageReader

            if not is_svg:
                image = ImageReader(BytesIO(image_bytes))
                cls._draw_signature(c, image, x, y, width, height)
                return True
        except Exception:
            if not is_svg:
                return False

        if is_svg:
            try:
                import cairosvg
                from reportlab.lib.utils import ImageReader

                png_bytes = cairosvg.svg2png(
                    bytestring=image_bytes, output_width=max(1, int(width * 3))
                )
                image = ImageReader(BytesIO(png_bytes))
                cls._draw_signature(c, image, x, y, width, height)
                return True
            except Exception:
                return False

        return False

    @classmethod
    def _draw_signature_image_from_path(
        cls,
        c: Any,
        image_path: Path,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        try:
            from reportlab.lib.utils import ImageReader

            image = ImageReader(str(image_path))
            cls._draw_signature(c, image, x, y, width, height)
            return
        except Exception:
            pass

        if image_path.suffix.lower() != ".svg":
            return

        try:
            import cairosvg
            from reportlab.lib.utils import ImageReader

            png_bytes = cairosvg.svg2png(url=str(image_path), output_width=max(1, int(width * 3)))
            image = ImageReader(BytesIO(png_bytes))
            cls._draw_signature(c, image, x, y, width, height)
        except Exception:
            return

    @staticmethod
    def _resolve_public_asset_path(path_value: str | None) -> Path | None:
        if not path_value:
            return None

        root = Path(__file__).resolve().parents[2]
        normalized = path_value.lstrip("/").strip()
        if not normalized:
            return None

        candidates = [
            root / normalized,
            root / "frontend" / normalized,
            root / "frontend" / "public" / normalized,
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return None
