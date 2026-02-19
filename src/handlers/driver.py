from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.driver import Driver
from src.schemas.driver import DriverCreate


class DriverHandler:
    async def list_drivers(self, session: AsyncSession, transport_company_id: int) -> list[Driver]:
        stmt: Select[tuple[Driver]] = (
            select(Driver)
            .where(Driver.transport_company_id == transport_company_id)
            .order_by(Driver.name.asc(), Driver.id.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_driver(
        self, session: AsyncSession, transport_company_id: int, payload: DriverCreate
    ) -> Driver:
        values = payload.model_dump()
        values["transport_company_id"] = transport_company_id
        driver = Driver(**values)
        session.add(driver)
        await session.commit()
        await session.refresh(driver)
        return driver
