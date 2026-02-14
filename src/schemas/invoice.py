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
    format_key: str = Field(default="standard", max_length=50)
    trip_ids: list[int] = Field(default_factory=list)


class InvoiceRead(ORMModel):
    id: int
    company_id: int
    start_date: date
    end_date: date
    due_date: date
    format_key: str
    total_amount: Decimal
    generated_at: datetime
    paid_at: datetime | None
    status: str


class InvoiceMarkPaid(ORMModel):
    paid_at: datetime | None = None
