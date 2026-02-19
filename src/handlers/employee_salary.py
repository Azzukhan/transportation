from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.employee_salary import EmployeeSalary
from src.schemas.employee_salary import (
    EmployeeSalaryCreate,
    EmployeeSalaryImportResult,
    EmployeeSalaryImportSkipped,
    EmployeeSalaryUpdate,
)
from src.services.employee_salary_excel import (
    ParsedEmployeeSalaryRow,
    ParsedEmployeeSalarySkippedRow,
)


class EmployeeSalaryHandler:
    async def list_employees(
        self,
        session: AsyncSession,
        transport_company_id: int,
    ) -> list[EmployeeSalary]:
        stmt: Select[tuple[EmployeeSalary]] = (
            select(EmployeeSalary)
            .where(EmployeeSalary.transport_company_id == transport_company_id)
            .order_by(EmployeeSalary.id.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_employee(
        self,
        session: AsyncSession,
        transport_company_id: int,
        employee_id: int,
    ) -> EmployeeSalary:
        stmt: Select[tuple[EmployeeSalary]] = (
            select(EmployeeSalary)
            .where(EmployeeSalary.id == employee_id)
            .where(EmployeeSalary.transport_company_id == transport_company_id)
        )
        result = await session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            raise AppException("Employee not found", status_code=404)
        return employee

    async def create_employee(
        self,
        session: AsyncSession,
        transport_company_id: int,
        payload: EmployeeSalaryCreate,
    ) -> EmployeeSalary:
        values = payload.model_dump()
        values["transport_company_id"] = transport_company_id
        values["total_payment"] = self._resolve_total(
            fixed=values.get("fixed_portion", Decimal("0.00")),
            variable=values.get("variable_portion", Decimal("0.00")),
            explicit_total=values.get("total_payment"),
        )
        employee = EmployeeSalary(**values)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        return employee

    async def update_employee(
        self,
        session: AsyncSession,
        transport_company_id: int,
        employee_id: int,
        payload: EmployeeSalaryUpdate,
    ) -> EmployeeSalary:
        employee = await self.get_employee(session, transport_company_id, employee_id)
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(employee, key, value)

        if {"fixed_portion", "variable_portion", "total_payment"} & set(updates.keys()):
            employee.total_payment = self._resolve_total(
                fixed=employee.fixed_portion,
                variable=employee.variable_portion,
                explicit_total=updates.get("total_payment"),
            )

        await session.commit()
        await session.refresh(employee)
        return employee

    async def delete_employee(
        self,
        session: AsyncSession,
        transport_company_id: int,
        employee_id: int,
    ) -> None:
        employee = await self.get_employee(session, transport_company_id, employee_id)
        await session.delete(employee)
        await session.commit()

    async def import_employees(
        self,
        session: AsyncSession,
        transport_company_id: int,
        rows: list[ParsedEmployeeSalaryRow],
        skipped_rows: list[ParsedEmployeeSalarySkippedRow] | None = None,
    ) -> EmployeeSalaryImportResult:
        existing = await self.list_employees(session, transport_company_id)
        by_identity: dict[tuple[str, str], EmployeeSalary] = {
            (item.work_permit_no, item.personal_no): item for item in existing
        }

        created = 0
        updated = 0
        skipped: list[EmployeeSalaryImportSkipped] = []
        for item in skipped_rows or []:
            skipped.append(
                EmployeeSalaryImportSkipped(row_number=item.row_number, reason=item.reason)
            )

        for row in rows:
            if len(row.work_permit_no) != 8:
                skipped.append(
                    EmployeeSalaryImportSkipped(
                        row_number=row.row_number, reason="work_permit_no must be 8 digits"
                    )
                )
                continue
            if len(row.personal_no) != 14:
                skipped.append(
                    EmployeeSalaryImportSkipped(
                        row_number=row.row_number, reason="personal_no must be 14 digits"
                    )
                )
                continue

            key = (row.work_permit_no, row.personal_no)
            total_payment = self._resolve_total(
                fixed=row.fixed_portion,
                variable=row.variable_portion,
                explicit_total=row.total_payment,
            )
            existing_row = by_identity.get(key)
            if existing_row is None:
                employee = EmployeeSalary(
                    transport_company_id=transport_company_id,
                    employee_name=row.employee_name,
                    work_permit_no=row.work_permit_no,
                    personal_no=row.personal_no,
                    bank_name_routing_no=row.bank_name_routing_no,
                    bank_account_no=row.bank_account_no,
                    days_absent=row.days_absent,
                    fixed_portion=row.fixed_portion,
                    variable_portion=row.variable_portion,
                    total_payment=total_payment,
                    on_leave=row.on_leave,
                )
                session.add(employee)
                by_identity[key] = employee
                created += 1
                continue

            existing_row.employee_name = row.employee_name
            existing_row.bank_name_routing_no = row.bank_name_routing_no
            existing_row.bank_account_no = row.bank_account_no
            existing_row.days_absent = row.days_absent
            existing_row.fixed_portion = row.fixed_portion
            existing_row.variable_portion = row.variable_portion
            existing_row.total_payment = total_payment
            existing_row.on_leave = row.on_leave
            updated += 1

        if created == 0 and updated == 0:
            raise AppException("No valid rows to import", status_code=400)

        await session.commit()
        return EmployeeSalaryImportResult(created=created, updated=updated, skipped=skipped)

    @staticmethod
    def _resolve_total(
        fixed: Decimal,
        variable: Decimal,
        explicit_total: Decimal | None,
    ) -> Decimal:
        if explicit_total is not None:
            return explicit_total.quantize(Decimal("0.01"))
        return (fixed + variable).quantize(Decimal("0.01"))
