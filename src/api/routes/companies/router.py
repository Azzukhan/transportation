from fastapi import APIRouter, status

from src.api.deps import CurrentAdminDep, DBSessionDep
from src.handlers.company import CompanyHandler
from src.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])
handler = CompanyHandler()


@router.get("", response_model=list[CompanyRead])
async def list_companies(
    session: DBSessionDep, current_admin: CurrentAdminDep
) -> list[CompanyRead]:
    companies = await handler.list_companies(session, current_admin.transport_company_id)
    return [CompanyRead.model_validate(entity) for entity in companies]


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> CompanyRead:
    company = await handler.create_company(session, current_admin.transport_company_id, payload)
    return CompanyRead.model_validate(company)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: int,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> CompanyRead:
    company = await handler.get_company(session, current_admin.transport_company_id, company_id)
    return CompanyRead.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int,
    payload: CompanyUpdate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> CompanyRead:
    company = await handler.update_company(
        session, current_admin.transport_company_id, company_id, payload
    )
    return CompanyRead.model_validate(company)
