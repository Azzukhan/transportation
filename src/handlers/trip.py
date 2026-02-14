from decimal import Decimal

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.company import Company
from src.models.trip import Trip
from src.schemas.trip import TripCreate, TripUpdate
from src.services.trip import TripService


class TripHandler:
    async def list_trips(self, session: AsyncSession, company_id: int | None = None) -> list[Trip]:
        stmt: Select[tuple[Trip]] = select(Trip)
        if company_id is not None:
            stmt = stmt.where(Trip.company_id == company_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_trip(self, session: AsyncSession, trip_id: int) -> Trip:
        trip = await session.get(Trip, trip_id)
        if trip is None:
            raise AppException("Trip not found", status_code=404)
        return trip

    async def create_trip(self, session: AsyncSession, payload: TripCreate) -> Trip:
        company = await session.get(Company, payload.company_id)
        if company is None:
            raise AppException("Company not found", status_code=404)

        trip = Trip(**payload.model_dump())
        TripService.apply_trip_amounts(trip)
        company.unpaid_amount = company.unpaid_amount + trip.total_amount

        session.add(trip)
        await session.commit()
        await session.refresh(trip)
        return trip

    async def update_trip(self, session: AsyncSession, trip_id: int, payload: TripUpdate) -> Trip:
        trip = await self.get_trip(session, trip_id)
        company = await session.get(Company, trip.company_id)
        if company is None:
            raise AppException("Company not found", status_code=404)

        old_total = trip.total_amount
        updates = payload.model_dump(exclude_none=True)

        for key, value in updates.items():
            setattr(trip, key, value)

        TripService.apply_trip_amounts(trip)
        delta = trip.total_amount - old_total
        company.unpaid_amount = company.unpaid_amount + delta

        await session.commit()
        await session.refresh(trip)
        return trip

    async def delete_trip(self, session: AsyncSession, trip_id: int) -> None:
        trip = await self.get_trip(session, trip_id)
        company = await session.get(Company, trip.company_id)
        if company is not None:
            adjustment = trip.total_amount if not trip.paid else Decimal("0.00")
            company.unpaid_amount = company.unpaid_amount - adjustment

        await session.delete(trip)
        await session.commit()
