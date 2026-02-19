import csv
from collections import defaultdict
from datetime import date
from io import StringIO

from fastapi import APIRouter, Query, Request, Response, status
from sqlalchemy import Select, select

from src.api.deps import CurrentAdminDep, DBSessionDep, SettingsDep
from src.core.audit import audit_event, enforce_sensitive_export_step_up
from src.core.exceptions import AppException
from src.handlers.trip import TripHandler
from src.models.company import Company
from src.models.driver import Driver
from src.schemas.trip import TripCreate, TripRead, TripUpdate

router = APIRouter(prefix="/trips", tags=["trips"])
handler = TripHandler()


@router.get("", response_model=list[TripRead])
async def list_trips(
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    company_id: int | None = Query(default=None),
    paid: bool | None = Query(default=None),
    driver_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> list[TripRead]:
    trips = await handler.list_trips(
        session,
        current_admin.transport_company_id,
        company_id,
        paid,
        driver_id,
        start_date,
        end_date,
    )
    return [TripRead.model_validate(entity) for entity in trips]


@router.get("/driver-report")
async def driver_report(
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    driver_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> list[dict[str, str | int]]:
    trips = await handler.list_trips(
        session=session,
        transport_company_id=current_admin.transport_company_id,
        company_id=None,
        paid=None,
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
    )

    grouped: dict[str, dict[str, int | str | float]] = defaultdict(
        lambda: {"trip_count": 0, "amount_excl_vat_total": 0.0}
    )
    for trip in trips:
        key = trip.driver
        grouped[key]["driver_name"] = key
        grouped[key]["trip_count"] = int(grouped[key]["trip_count"]) + 1
        grouped[key]["amount_excl_vat_total"] = float(
            grouped[key]["amount_excl_vat_total"]
        ) + float(trip.amount)

    rows = sorted(grouped.values(), key=lambda item: str(item["driver_name"]).lower())
    return [
        {
            "driver_name": str(row["driver_name"]),
            "trip_count": int(row["trip_count"]),
            "amount_excl_vat_total": f"{float(row['amount_excl_vat_total']):.2f}",
        }
        for row in rows
    ]


@router.get("/driver-report/export")
async def export_driver_report(
    request: Request,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
    settings: SettingsDep,
    driver_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> Response:
    enforce_sensitive_export_step_up(request, settings)
    if driver_id is not None:
        driver_stmt: Select[tuple[Driver]] = (
            select(Driver)
            .where(Driver.id == driver_id)
            .where(Driver.transport_company_id == current_admin.transport_company_id)
        )
        driver_result = await session.execute(driver_stmt)
        if driver_result.scalar_one_or_none() is None:
            raise AppException("Driver not found", status_code=404)

    trips = await handler.list_trips(
        session=session,
        transport_company_id=current_admin.transport_company_id,
        company_id=None,
        paid=None,
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
    )

    company_ids = sorted({trip.company_id for trip in trips})
    company_name_by_id: dict[int, str] = {}
    if company_ids:
        stmt: Select[tuple[Company]] = (
            select(Company)
            .where(Company.id.in_(company_ids))
            .where(Company.transport_company_id == current_admin.transport_company_id)
        )
        company_result = await session.execute(stmt)
        company_name_by_id = {
            company.id: company.name for company in company_result.scalars().all()
        }

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Trip ID",
            "Date",
            "Driver",
            "Company Name",
            "Origin",
            "Destination",
            "Amount (AED, excl. VAT)",
        ]
    )
    total = 0.0
    for trip in trips:
        amount = float(trip.amount)
        total += amount
        writer.writerow(
            [
                trip.id,
                trip.date.isoformat(),
                trip.driver,
                company_name_by_id.get(trip.company_id, f"Company #{trip.company_id}"),
                trip.origin,
                trip.destination,
                f"{amount:.2f}",
            ]
        )
    writer.writerow([])
    writer.writerow(["", "", "", "", "", "Total", f"{total:.2f}"])

    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="driver_report",
        action="export",
        metadata={
            "driver_id": driver_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "trip_count": len(trips),
        },
    )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="driver_report.csv"'},
    )


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
async def create_trip(
    payload: TripCreate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> TripRead:
    trip = await handler.create_trip(session, current_admin.transport_company_id, payload)
    return TripRead.model_validate(trip)


@router.get("/{trip_id}", response_model=TripRead)
async def get_trip(
    trip_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> TripRead:
    trip = await handler.get_trip(session, current_admin.transport_company_id, trip_id)
    return TripRead.model_validate(trip)


@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: int,
    payload: TripUpdate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> TripRead:
    trip = await handler.update_trip(session, current_admin.transport_company_id, trip_id, payload)
    return TripRead.model_validate(trip)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> Response:
    await handler.delete_trip(session, current_admin.transport_company_id, trip_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
