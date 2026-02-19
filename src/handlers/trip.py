from datetime import date
from decimal import Decimal

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.company import Company
from src.models.driver import Driver
from src.models.trip import Trip
from src.schemas.trip import TripCreate, TripUpdate
from src.services.trip import TripService


class TripHandler:
    async def list_trips(
        self,
        session: AsyncSession,
        transport_company_id: int,
        company_id: int | None = None,
        paid: bool | None = None,
        driver_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Trip]:
        stmt: Select[tuple[Trip]] = select(Trip).where(
            Trip.transport_company_id == transport_company_id
        )
        if company_id is not None:
            stmt = stmt.where(Trip.company_id == company_id)
        if paid is not None:
            stmt = stmt.where(Trip.paid.is_(paid))
        if driver_id is not None:
            stmt = stmt.where(Trip.driver_id == driver_id)
        if start_date is not None:
            stmt = stmt.where(Trip.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Trip.date <= end_date)
        stmt = stmt.order_by(Trip.date.desc(), Trip.id.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_trip(
        self, session: AsyncSession, transport_company_id: int, trip_id: int
    ) -> Trip:
        stmt: Select[tuple[Trip]] = (
            select(Trip)
            .where(Trip.id == trip_id)
            .where(Trip.transport_company_id == transport_company_id)
        )
        result = await session.execute(stmt)
        trip = result.scalar_one_or_none()
        if trip is None:
            raise AppException("Trip not found", status_code=404)
        return trip

    async def create_trip(
        self, session: AsyncSession, transport_company_id: int, payload: TripCreate
    ) -> Trip:
        company = await session.get(Company, payload.company_id)
        if company is None or company.transport_company_id != transport_company_id:
            raise AppException("Company not found", status_code=404)

        values = payload.model_dump()
        values["transport_company_id"] = transport_company_id
        values = await self._normalize_driver_payload(session, transport_company_id, values)
        values["trip_category"] = self._normalize_trip_category(
            str(values.get("trip_category") or "")
        )
        trip = Trip(**values)
        TripService.apply_trip_amounts(trip)
        company.unpaid_amount = company.unpaid_amount + trip.total_amount

        session.add(trip)
        await session.commit()
        await session.refresh(trip)
        return trip

    async def update_trip(
        self,
        session: AsyncSession,
        transport_company_id: int,
        trip_id: int,
        payload: TripUpdate,
    ) -> Trip:
        trip = await self.get_trip(session, transport_company_id, trip_id)
        company = await session.get(Company, trip.company_id)
        if company is None or company.transport_company_id != transport_company_id:
            raise AppException("Company not found", status_code=404)

        old_total = trip.total_amount
        updates = payload.model_dump(exclude_none=True)
        if "trip_category" in updates:
            updates["trip_category"] = self._normalize_trip_category(updates["trip_category"])

        if any(
            key in updates
            for key in ("driver_id", "external_driver_name", "external_driver_mobile", "driver")
        ):
            current: dict[str, object] = {
                "driver_id": trip.driver_id,
                "external_driver_name": trip.external_driver_name,
                "external_driver_mobile": trip.external_driver_mobile,
                "driver": trip.driver,
            }
            current.update(updates)
            updates.update(
                await self._normalize_driver_payload(session, transport_company_id, current)
            )

        for key, value in updates.items():
            setattr(trip, key, value)

        TripService.apply_trip_amounts(trip)
        delta = trip.total_amount - old_total
        company.unpaid_amount = company.unpaid_amount + delta

        await session.commit()
        await session.refresh(trip)
        return trip

    async def delete_trip(
        self, session: AsyncSession, transport_company_id: int, trip_id: int
    ) -> None:
        trip = await self.get_trip(session, transport_company_id, trip_id)
        company = await session.get(Company, trip.company_id)
        if company is not None:
            adjustment = trip.total_amount if not trip.paid else Decimal("0.00")
            company.unpaid_amount = company.unpaid_amount - adjustment

        await session.delete(trip)
        await session.commit()

    @staticmethod
    def _normalize_trip_category(value: str | None) -> str:
        category = (value or "domestic").strip().lower()
        if category not in {"domestic", "international"}:
            raise AppException("trip_category must be domestic or international", status_code=400)
        return category

    async def _normalize_driver_payload(
        self,
        session: AsyncSession,
        transport_company_id: int,
        values: dict[str, object],
    ) -> dict[str, object]:
        driver_id = values.get("driver_id")
        external_name = str(values.get("external_driver_name") or "").strip()
        external_mobile = str(values.get("external_driver_mobile") or "").strip()
        manual_driver = str(values.get("driver") or "").strip()

        if isinstance(driver_id, int):
            driver = await session.get(Driver, driver_id)
            if driver is None or driver.transport_company_id != transport_company_id:
                raise AppException("Selected driver not found", status_code=404)
            values["driver"] = driver.name
            values["driver_id"] = driver.id
            values["external_driver_name"] = None
            values["external_driver_mobile"] = None
            return values

        if external_name:
            values["driver"] = external_name
            values["driver_id"] = None
            values["external_driver_name"] = external_name
            values["external_driver_mobile"] = external_mobile or None
            return values

        if manual_driver:
            values["driver"] = manual_driver
            values["driver_id"] = None
            values["external_driver_name"] = None
            values["external_driver_mobile"] = None
            return values

        raise AppException("Driver is required", status_code=400)
