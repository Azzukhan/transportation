from fastapi import APIRouter, Query, Response, status

from src.api.deps import DBSessionDep
from src.handlers.trip import TripHandler
from src.schemas.trip import TripCreate, TripRead, TripUpdate

router = APIRouter(prefix="/trips", tags=["trips"])
handler = TripHandler()


@router.get("", response_model=list[TripRead])
async def list_trips(
    session: DBSessionDep,
    company_id: int | None = Query(default=None),
) -> list[TripRead]:
    trips = await handler.list_trips(session, company_id)
    return [TripRead.model_validate(entity) for entity in trips]


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
async def create_trip(
    payload: TripCreate,
    session: DBSessionDep,
) -> TripRead:
    trip = await handler.create_trip(session, payload)
    return TripRead.model_validate(trip)


@router.get("/{trip_id}", response_model=TripRead)
async def get_trip(
    trip_id: int,
    session: DBSessionDep,
) -> TripRead:
    trip = await handler.get_trip(session, trip_id)
    return TripRead.model_validate(trip)


@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: int,
    payload: TripUpdate,
    session: DBSessionDep,
) -> TripRead:
    trip = await handler.update_trip(session, trip_id, payload)
    return TripRead.model_validate(trip)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: int,
    session: DBSessionDep,
) -> Response:
    await handler.delete_trip(session, trip_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
