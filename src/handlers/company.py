from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.company import Company
from src.schemas.company import CompanyCreate, CompanyUpdate


class CompanyHandler:
    async def list_companies(
        self, session: AsyncSession, transport_company_id: int
    ) -> list[Company]:
        stmt: Select[tuple[Company]] = (
            select(Company)
            .where(Company.transport_company_id == transport_company_id)
            .order_by(Company.id.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_company(
        self,
        session: AsyncSession,
        transport_company_id: int,
        payload: CompanyCreate,
    ) -> Company:
        data = payload.model_dump()
        data["transport_company_id"] = transport_company_id
        data["paid_amount"] = 0
        data["unpaid_amount"] = 0
        company = Company(**data)
        session.add(company)
        await session.commit()
        await session.refresh(company)
        return company

    async def get_company(
        self, session: AsyncSession, transport_company_id: int, company_id: int
    ) -> Company:
        stmt: Select[tuple[Company]] = (
            select(Company)
            .where(Company.id == company_id)
            .where(Company.transport_company_id == transport_company_id)
        )
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()
        if company is None:
            raise AppException("Company not found", status_code=404)
        return company

    async def update_company(
        self,
        session: AsyncSession,
        transport_company_id: int,
        company_id: int,
        payload: CompanyUpdate,
    ) -> Company:
        company = await self.get_company(session, transport_company_id, company_id)
        updates = payload.model_dump(exclude_none=True)
        for key, value in updates.items():
            setattr(company, key, value)
        await session.commit()
        await session.refresh(company)
        return company
