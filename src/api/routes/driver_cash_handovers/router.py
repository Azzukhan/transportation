from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query, Request, status
from sqlalchemy import Select, select

from src.api.deps import CurrentAdminDep, DBSessionDep
from src.core.audit import audit_event
from src.handlers.driver_cash_handover import DriverCashHandoverHandler
from src.models.driver import Driver
from src.schemas.driver_cash_handover import (
    DriverCashHandoverCreate,
    DriverCashHandoverRead,
    DriverCashSummaryRow,
)

router = APIRouter(prefix="/driver-cash-handovers", tags=["driver-cash-handovers"])
handler = DriverCashHandoverHandler()


@router.get("", response_model=list[DriverCashHandoverRead])
async def list_driver_cash_handovers(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    driver_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> list[DriverCashHandoverRead]:
    rows = await handler.list_handovers(
        session,
        current_admin.transport_company_id,
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
    )
    driver_ids = sorted({item.driver_id for item in rows})
    name_by_id: dict[int, str] = {}
    if driver_ids:
        stmt: Select[tuple[Driver]] = (
            select(Driver)
            .where(Driver.id.in_(driver_ids))
            .where(Driver.transport_company_id == current_admin.transport_company_id)
        )
        result = await session.execute(stmt)
        name_by_id = {driver.id: driver.name for driver in result.scalars().all()}

    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="driver_cash_handover",
        action="list",
        metadata={"count": len(rows), "driver_id": driver_id},
    )
    return [
        DriverCashHandoverRead(
            id=item.id,
            driver_id=item.driver_id,
            driver_name=name_by_id.get(item.driver_id, f"Driver #{item.driver_id}"),
            handover_date=item.handover_date,
            amount=item.amount,
            notes=item.notes,
        )
        for item in rows
    ]


@router.post("", response_model=DriverCashHandoverRead, status_code=status.HTTP_201_CREATED)
async def create_driver_cash_handover(
    request: Request,
    payload: DriverCashHandoverCreate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> DriverCashHandoverRead:
    row = await handler.create_handover(session, current_admin.transport_company_id, payload)
    driver = await session.get(Driver, row.driver_id)
    driver_name = driver.name if driver is not None else f"Driver #{row.driver_id}"
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="driver_cash_handover",
        resource_id=str(row.id),
        action="create",
        metadata={"driver_id": row.driver_id, "amount": str(row.amount)},
    )
    return DriverCashHandoverRead(
        id=row.id,
        driver_id=row.driver_id,
        driver_name=driver_name,
        handover_date=row.handover_date,
        amount=row.amount,
        notes=row.notes,
    )


@router.get("/summary", response_model=list[DriverCashSummaryRow])
async def summarize_driver_cash(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    driver_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> list[DriverCashSummaryRow]:
    rows = await handler.summary_by_driver(
        session,
        current_admin.transport_company_id,
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
    )
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="driver_cash_handover",
        action="summary_read",
        metadata={"count": len(rows), "driver_id": driver_id},
    )
    return rows
