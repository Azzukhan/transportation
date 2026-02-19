from fastapi import APIRouter, Request, status

from src.api.deps import CurrentAdminDep, DBSessionDep
from src.handlers.public_request import PublicRequestHandler
from src.schemas.contact import ContactRequestCreate, ContactRequestRead, ContactRequestUpdate
from src.schemas.quote import QuoteRequestCreate, QuoteRequestRead, QuoteRequestUpdate

router = APIRouter(prefix="/public", tags=["public"])
handler = PublicRequestHandler()


@router.post(
    "/contact-requests", response_model=ContactRequestRead, status_code=status.HTTP_201_CREATED
)
async def create_contact_request(
    request: Request,
    payload: ContactRequestCreate,
    session: DBSessionDep,
) -> ContactRequestRead:
    transport_company_id = await handler.resolve_transport_company_id(session, request)
    contact = await handler.create_contact_request(session, transport_company_id, payload)
    return ContactRequestRead.model_validate(contact)


@router.get("/contact-requests", response_model=list[ContactRequestRead])
async def list_contact_requests(
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> list[ContactRequestRead]:
    requests = await handler.list_contact_requests(session, current_admin.transport_company_id)
    return [ContactRequestRead.model_validate(item) for item in requests]


@router.patch("/contact-requests/{request_id}", response_model=ContactRequestRead)
async def update_contact_request(
    request_id: int,
    payload: ContactRequestUpdate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> ContactRequestRead:
    updated = await handler.update_contact_request(
        session, current_admin.transport_company_id, request_id, payload
    )
    return ContactRequestRead.model_validate(updated)


@router.post(
    "/quote-requests", response_model=QuoteRequestRead, status_code=status.HTTP_201_CREATED
)
async def create_quote_request(
    request: Request,
    payload: QuoteRequestCreate,
    session: DBSessionDep,
) -> QuoteRequestRead:
    transport_company_id = await handler.resolve_transport_company_id(session, request)
    quote = await handler.create_quote_request(session, transport_company_id, payload)
    return QuoteRequestRead.model_validate(quote)


@router.get("/quote-requests", response_model=list[QuoteRequestRead])
async def list_quote_requests(
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> list[QuoteRequestRead]:
    requests = await handler.list_quote_requests(session, current_admin.transport_company_id)
    return [QuoteRequestRead.model_validate(item) for item in requests]


@router.patch("/quote-requests/{request_id}", response_model=QuoteRequestRead)
async def update_quote_request(
    request_id: int,
    payload: QuoteRequestUpdate,
    session: DBSessionDep,
    current_admin: CurrentAdminDep,
) -> QuoteRequestRead:
    updated = await handler.update_quote_request(
        session, current_admin.transport_company_id, request_id, payload
    )
    return QuoteRequestRead.model_validate(updated)
