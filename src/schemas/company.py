from decimal import Decimal

from pydantic import EmailStr, Field

from src.schemas.common import ORMModel


class CompanyBase(ORMModel):
    name: str = Field(max_length=255)
    address: str
    email: EmailStr
    phone: str = Field(max_length=20)
    trn: str = Field(max_length=30)
    contact_person: str = Field(max_length=25)
    po_box: str = Field(max_length=20)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(ORMModel):
    name: str | None = Field(default=None, max_length=255)
    address: str | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    trn: str | None = Field(default=None, max_length=30)
    contact_person: str | None = Field(default=None, max_length=25)
    po_box: str | None = Field(default=None, max_length=20)


class CompanyRead(CompanyBase):
    id: int
    paid_amount: Decimal
    unpaid_amount: Decimal
