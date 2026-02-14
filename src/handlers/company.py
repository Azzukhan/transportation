from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.db.db_handler import GenericDBHandler
from src.models.company import Company
from src.schemas.company import CompanyCreate, CompanyUpdate


class CompanyHandler:
    def __init__(self) -> None:
        self.db = GenericDBHandler(Company)

    async def list_companies(self, session: AsyncSession) -> list[Company]:
        return await self.db.list(session)

    async def create_company(self, session: AsyncSession, payload: CompanyCreate) -> Company:
        data = payload.model_dump()
        data["paid_amount"] = 0
        data["unpaid_amount"] = 0
        return await self.db.create(session, data)

    async def get_company(self, session: AsyncSession, company_id: int) -> Company:
        company = await self.db.get(session, company_id)
        if company is None:
            raise AppException("Company not found", status_code=404)
        return company

    async def update_company(
        self,
        session: AsyncSession,
        company_id: int,
        payload: CompanyUpdate,
    ) -> Company:
        company = await self.get_company(session, company_id)
        updates = payload.model_dump(exclude_none=True)
        return await self.db.update(session, company, updates)
