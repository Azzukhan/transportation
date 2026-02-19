from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import Field

from src.schemas.common import ORMModel


class InvoiceCreate(ORMModel):
    company_id: int
    start_date: date | None = None
    end_date: date | None = None
    due_date: date | None = None
    invoice_number: str | None = Field(default=None, max_length=60)
    prepared_by_mode: str = Field(default="without_signature", max_length=25)
    signatory_id: int | None = None
    format_key: str = Field(default="standard", max_length=50)
    trip_ids: list[int] = Field(default_factory=list)


class InvoiceRead(ORMModel):
    id: int
    company_id: int
    start_date: date
    end_date: date
    due_date: date
    invoice_number: str | None
    format_key: str
    prepared_by_mode: str
    signatory_id: int | None
    signatory_name: str | None
    signatory_image_path: str | None
    signatory_image_mime: str | None
    total_amount: Decimal
    generated_at: datetime
    paid_at: datetime | None
    status: str


class InvoiceMarkPaid(ORMModel):
    paid_at: datetime | None = None


class SignatoryRead(ORMModel):
    id: int
    name: str
    signature_image_mime: str | None
    has_signature: bool
