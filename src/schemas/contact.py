from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from src.schemas.common import ORMModel


class ContactRequestCreate(ORMModel):
    name: str = Field(max_length=120)
    email: EmailStr
    phone: str = Field(max_length=40)
    subject: str = Field(max_length=160)
    message: str = Field(min_length=5)
    source_page: str = Field(default="contact", max_length=40)


class ContactRequestUpdate(ORMModel):
    status: str = Field(max_length=20)


class ContactRequestRead(ORMModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    subject: str
    message: str
    status: str
    source_page: str
    created_at: datetime
    updated_at: datetime
