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
    destination_company_name: str | None = Field(default=None, max_length=255)
    trip_category: str = Field(default="domestic", max_length=20)
    amount: Decimal
    toll_gate: Decimal = Decimal("0.00")
    driver: str = Field(max_length=30)
    driver_id: int | None = None
    external_driver_name: str | None = Field(default=None, max_length=120)
    external_driver_mobile: str | None = Field(default=None, max_length=25)


class TripCreate(TripBase):
    pass


class TripUpdate(ORMModel):
    date: dt.date | None = None
    freight: str | None = Field(default=None, max_length=25)
    origin: str | None = Field(default=None, max_length=255)
    destination: str | None = Field(default=None, max_length=255)
    destination_company_name: str | None = Field(default=None, max_length=255)
    trip_category: str | None = Field(default=None, max_length=20)
    amount: Decimal | None = None
    toll_gate: Decimal | None = None
    driver: str | None = Field(default=None, max_length=30)
    driver_id: int | None = None
    external_driver_name: str | None = Field(default=None, max_length=120)
    external_driver_mobile: str | None = Field(default=None, max_length=25)
    paid: bool | None = None


class TripRead(TripBase):
    id: int
    vat: Decimal
    total_amount: Decimal
    paid: bool
    invoice_id: int | None
