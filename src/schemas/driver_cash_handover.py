from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pydantic import Field

from src.schemas.common import ORMModel


class DriverCashHandoverCreate(ORMModel):
    driver_id: int
    handover_date: dt.date
    amount: Decimal = Field(gt=0)
    notes: str | None = Field(default=None, max_length=255)


class DriverCashHandoverRead(ORMModel):
    id: int
    driver_id: int
    driver_name: str
    handover_date: dt.date
    amount: Decimal
    notes: str | None


class DriverCashSummaryRow(ORMModel):
    driver_id: int
    driver_name: str
    trip_count: int
    earned_amount_total: Decimal
    handover_amount_total: Decimal
    balance_amount: Decimal
