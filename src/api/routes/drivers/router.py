from fastapi import APIRouter, status

from src.api.deps import CurrentAdminDep, DBSessionDep
from src.handlers.driver import DriverHandler
from src.schemas.driver import DriverCreate, DriverRead

router = APIRouter(prefix="/drivers", tags=["drivers"])
handler = DriverHandler()


@router.get("", response_model=list[DriverRead])
async def list_drivers(
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> list[DriverRead]:
    drivers = await handler.list_drivers(session, current_admin.transport_company_id)
    return [DriverRead.model_validate(entity) for entity in drivers]


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
async def create_driver(
    payload: DriverCreate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> DriverRead:
    driver = await handler.create_driver(session, current_admin.transport_company_id, payload)
    return DriverRead.model_validate(driver)
