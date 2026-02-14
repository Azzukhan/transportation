from fastapi import APIRouter, status

from src.api.deps import CurrentSubjectDep, DBSessionDep
from src.handlers.public_request import PublicRequestHandler
from src.schemas.contact import ContactRequestCreate, ContactRequestRead, ContactRequestUpdate
from src.schemas.quote import QuoteRequestCreate, QuoteRequestRead, QuoteRequestUpdate

router = APIRouter(prefix="/public", tags=["public"])
handler = PublicRequestHandler()


@router.post("/contact-requests", response_model=ContactRequestRead, status_code=status.HTTP_201_CREATED)
async def create_contact_request(
    payload: ContactRequestCreate,
    session: DBSessionDep,
) -> ContactRequestRead:
    contact = await handler.create_contact_request(session, payload)
    return ContactRequestRead.model_validate(contact)


@router.get("/contact-requests", response_model=list[ContactRequestRead])
async def list_contact_requests(
    session: DBSessionDep,
    _: CurrentSubjectDep,
) -> list[ContactRequestRead]:
    requests = await handler.list_contact_requests(session)
    return [ContactRequestRead.model_validate(item) for item in requests]


@router.patch("/contact-requests/{request_id}", response_model=ContactRequestRead)
async def update_contact_request(
    request_id: int,
    payload: ContactRequestUpdate,
    session: DBSessionDep,
    _: CurrentSubjectDep,
) -> ContactRequestRead:
    updated = await handler.update_contact_request(session, request_id, payload)
    return ContactRequestRead.model_validate(updated)


@router.post("/quote-requests", response_model=QuoteRequestRead, status_code=status.HTTP_201_CREATED)
async def create_quote_request(
    payload: QuoteRequestCreate,
    session: DBSessionDep,
) -> QuoteRequestRead:
    quote = await handler.create_quote_request(session, payload)
    return QuoteRequestRead.model_validate(quote)


@router.get("/quote-requests", response_model=list[QuoteRequestRead])
async def list_quote_requests(
    session: DBSessionDep,
    _: CurrentSubjectDep,
) -> list[QuoteRequestRead]:
    requests = await handler.list_quote_requests(session)
    return [QuoteRequestRead.model_validate(item) for item in requests]


@router.patch("/quote-requests/{request_id}", response_model=QuoteRequestRead)
async def update_quote_request(
    request_id: int,
    payload: QuoteRequestUpdate,
    session: DBSessionDep,
    _: CurrentSubjectDep,
) -> QuoteRequestRead:
    updated = await handler.update_quote_request(session, request_id, payload)
    return QuoteRequestRead.model_validate(updated)
