from __future__ import annotations

import datetime as dt

from pydantic import Field

from src.schemas.common import ORMModel


class DriverBase(ORMModel):
    name: str = Field(min_length=1, max_length=120)
    mobile_number: str = Field(min_length=1, max_length=25)
    passport_number: str | None = Field(default=None, max_length=40)
    emirates_id_number: str | None = Field(default=None, max_length=40)
    emirates_id_expiry_date: dt.date | None = None


class DriverCreate(DriverBase):
    pass


class DriverRead(DriverBase):
    id: int
