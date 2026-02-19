from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, BaseModel, IDMixin, TransportCompanyMixin

if TYPE_CHECKING:
    from src.models.transport_company import TransportCompany


class EmployeeSalary(IDMixin, TransportCompanyMixin, AuditMixin, BaseModel):
    __tablename__ = "employee_salaries"

    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    work_permit_no: Mapped[str] = mapped_column(String(8), nullable=False)
    personal_no: Mapped[str] = mapped_column(String(14), nullable=False)
    bank_name_routing_no: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bank_account_no: Mapped[str] = mapped_column(String(50), nullable=False)
    days_absent: Mapped[int | None] = mapped_column(nullable=True)
    fixed_portion: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    variable_portion: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    total_payment: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    on_leave: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    transport_company: Mapped[TransportCompany] = relationship(back_populates="employee_salaries")
