from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pydantic import Field

from src.schemas.common import ORMModel


class TripBase(ORMModel):
    company_id: int
    date: dt.date
    freight: str = Field(max_length=25)
    origin: str = Field(max_length=255)
    destination: str = Field(max_length=255)
    amount: Decimal
    toll_gate: Decimal = Decimal("0.00")
    driver: str = Field(max_length=30)


class TripCreate(TripBase):
    pass


class TripUpdate(ORMModel):
    date: dt.date | None = None
    freight: str | None = Field(default=None, max_length=25)
    origin: str | None = Field(default=None, max_length=255)
    destination: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = None
    toll_gate: Decimal | None = None
    driver: str | None = Field(default=None, max_length=30)
    paid: bool | None = None


class TripRead(TripBase):
    id: int
    vat: Decimal
    total_amount: Decimal
    paid: bool
    invoice_id: int | None
