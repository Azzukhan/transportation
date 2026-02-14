from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from src.schemas.common import ORMModel


class QuoteRequestCreate(ORMModel):
    name: str = Field(max_length=120)
    email: EmailStr
    mobile: str = Field(max_length=40)
    freight: str = Field(max_length=30)
    origin: str = Field(max_length=255)
    destination: str = Field(max_length=255)
    note: str = ""


class QuoteRequestUpdate(ORMModel):
    status: str = Field(max_length=20)


class QuoteRequestRead(ORMModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    freight: str
    origin: str
    destination: str
    note: str
    status: str
    created_at: datetime
    updated_at: datetime
