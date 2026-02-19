from __future__ import annotations

from decimal import Decimal

from pydantic import Field, field_validator

from src.schemas.common import ORMModel


class EmployeeSalaryBase(ORMModel):
    employee_name: str = Field(min_length=1, max_length=255)
    work_permit_no: str = Field(min_length=8, max_length=8)
    personal_no: str = Field(min_length=14, max_length=14)
    bank_name_routing_no: str | None = Field(default=None, max_length=255)
    bank_account_no: str = Field(min_length=1, max_length=50)
    days_absent: int | None = Field(default=None, ge=0, le=31)
    fixed_portion: Decimal = Field(default=Decimal("0.00"), ge=0)
    variable_portion: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_payment: Decimal = Field(default=Decimal("0.00"), ge=0)
    on_leave: bool = False

    @field_validator("work_permit_no")
    @classmethod
    def validate_work_permit_digits(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("work_permit_no must be numeric")
        return cleaned

    @field_validator("personal_no")
    @classmethod
    def validate_personal_no_digits(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("personal_no must be numeric")
        return cleaned

    @field_validator("total_payment")
    @classmethod
    def normalize_total_payment(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class EmployeeSalaryCreate(EmployeeSalaryBase):
    pass


class EmployeeSalaryUpdate(ORMModel):
    employee_name: str | None = Field(default=None, min_length=1, max_length=255)
    work_permit_no: str | None = Field(default=None, min_length=8, max_length=8)
    personal_no: str | None = Field(default=None, min_length=14, max_length=14)
    bank_name_routing_no: str | None = Field(default=None, max_length=255)
    bank_account_no: str | None = Field(default=None, min_length=1, max_length=50)
    days_absent: int | None = Field(default=None, ge=0, le=31)
    fixed_portion: Decimal | None = Field(default=None, ge=0)
    variable_portion: Decimal | None = Field(default=None, ge=0)
    total_payment: Decimal | None = Field(default=None, ge=0)
    on_leave: bool | None = None

    @field_validator("work_permit_no")
    @classmethod
    def validate_work_permit_digits(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("work_permit_no must be numeric")
        return cleaned

    @field_validator("personal_no")
    @classmethod
    def validate_personal_no_digits(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("personal_no must be numeric")
        return cleaned


class EmployeeSalaryRead(EmployeeSalaryBase):
    id: int


class EmployeeSalaryImportSkipped(ORMModel):
    row_number: int
    reason: str


class EmployeeSalaryImportResult(ORMModel):
    created: int
    updated: int
    skipped: list[EmployeeSalaryImportSkipped]
