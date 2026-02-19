from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.driver import Driver
from src.models.driver_cash_handover import DriverCashHandover
from src.models.trip import Trip
from src.schemas.driver_cash_handover import (
    DriverCashHandoverCreate,
    DriverCashSummaryRow,
)


@dataclass
class _SummaryAccumulator:
    trip_count: int = 0
    earned: Decimal = Decimal("0.00")
    handover: Decimal = Decimal("0.00")


class DriverCashHandoverHandler:
    async def list_handovers(
        self,
        session: AsyncSession,
        transport_company_id: int,
        driver_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DriverCashHandover]:
        stmt: Select[tuple[DriverCashHandover]] = (
            select(DriverCashHandover)
            .where(DriverCashHandover.transport_company_id == transport_company_id)
            .order_by(DriverCashHandover.handover_date.desc(), DriverCashHandover.id.desc())
        )
        if driver_id is not None:
            stmt = stmt.where(DriverCashHandover.driver_id == driver_id)
        if start_date is not None:
            stmt = stmt.where(DriverCashHandover.handover_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(DriverCashHandover.handover_date <= end_date)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_handover(
        self,
        session: AsyncSession,
        transport_company_id: int,
        payload: DriverCashHandoverCreate,
    ) -> DriverCashHandover:
        driver = await session.get(Driver, payload.driver_id)
        if driver is None or driver.transport_company_id != transport_company_id:
            raise AppException("Driver not found", status_code=404)

        handover = DriverCashHandover(
            transport_company_id=transport_company_id,
            driver_id=payload.driver_id,
            handover_date=payload.handover_date,
            amount=payload.amount.quantize(Decimal("0.01")),
            notes=(payload.notes or "").strip() or None,
        )
        session.add(handover)
        await session.commit()
        await session.refresh(handover)
        return handover

    async def summary_by_driver(
        self,
        session: AsyncSession,
        transport_company_id: int,
        driver_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DriverCashSummaryRow]:
        accum: dict[int, _SummaryAccumulator] = defaultdict(_SummaryAccumulator)

        trip_stmt: Select[tuple[Trip]] = (
            select(Trip)
            .where(Trip.transport_company_id == transport_company_id)
            .where(Trip.driver_id.is_not(None))
        )
        if driver_id is not None:
            trip_stmt = trip_stmt.where(Trip.driver_id == driver_id)
        if start_date is not None:
            trip_stmt = trip_stmt.where(Trip.date >= start_date)
        if end_date is not None:
            trip_stmt = trip_stmt.where(Trip.date <= end_date)
        trip_result = await session.execute(trip_stmt)
        for trip in trip_result.scalars().all():
            if trip.driver_id is None:
                continue
            rec = accum[trip.driver_id]
            rec.trip_count += 1
            rec.earned += trip.amount

        handover_stmt: Select[tuple[DriverCashHandover]] = select(DriverCashHandover).where(
            DriverCashHandover.transport_company_id == transport_company_id
        )
        if driver_id is not None:
            handover_stmt = handover_stmt.where(DriverCashHandover.driver_id == driver_id)
        if start_date is not None:
            handover_stmt = handover_stmt.where(DriverCashHandover.handover_date >= start_date)
        if end_date is not None:
            handover_stmt = handover_stmt.where(DriverCashHandover.handover_date <= end_date)
        handover_result = await session.execute(handover_stmt)
        for handover in handover_result.scalars().all():
            rec = accum[handover.driver_id]
            rec.handover += handover.amount

        if not accum:
            return []

        driver_ids = sorted(accum.keys())
        driver_stmt: Select[tuple[Driver]] = (
            select(Driver)
            .where(Driver.id.in_(driver_ids))
            .where(Driver.transport_company_id == transport_company_id)
        )
        driver_result = await session.execute(driver_stmt)
        names = {driver.id: driver.name for driver in driver_result.scalars().all()}

        rows = [
            DriverCashSummaryRow(
                driver_id=driver_key,
                driver_name=names.get(driver_key, f"Driver #{driver_key}"),
                trip_count=acc.trip_count,
                earned_amount_total=acc.earned.quantize(Decimal("0.01")),
                handover_amount_total=acc.handover.quantize(Decimal("0.01")),
                balance_amount=(acc.earned - acc.handover).quantize(Decimal("0.01")),
            )
            for driver_key, acc in accum.items()
        ]
        rows.sort(key=lambda item: item.driver_name.lower())
        return rows
