from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException
from src.models.contact_request import ContactRequest
from src.models.quote_request import QuoteRequest
from src.schemas.contact import ContactRequestCreate, ContactRequestUpdate
from src.schemas.quote import QuoteRequestCreate, QuoteRequestUpdate


class PublicRequestHandler:
    async def create_contact_request(
        self,
        session: AsyncSession,
        payload: ContactRequestCreate,
    ) -> ContactRequest:
        entity = ContactRequest(**payload.model_dump())
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def list_contact_requests(self, session: AsyncSession) -> list[ContactRequest]:
        stmt: Select[tuple[ContactRequest]] = select(ContactRequest).order_by(ContactRequest.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update_contact_request(
        self,
        session: AsyncSession,
        request_id: int,
        payload: ContactRequestUpdate,
    ) -> ContactRequest:
        entity = await session.get(ContactRequest, request_id)
        if entity is None:
            raise AppException("Contact request not found", status_code=404)

        entity.status = payload.status
        await session.commit()
        await session.refresh(entity)
        return entity

    async def create_quote_request(
        self,
        session: AsyncSession,
        payload: QuoteRequestCreate,
    ) -> QuoteRequest:
        entity = QuoteRequest(**payload.model_dump())
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def list_quote_requests(self, session: AsyncSession) -> list[QuoteRequest]:
        stmt: Select[tuple[QuoteRequest]] = select(QuoteRequest).order_by(QuoteRequest.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update_quote_request(
        self,
        session: AsyncSession,
        request_id: int,
        payload: QuoteRequestUpdate,
    ) -> QuoteRequest:
        entity = await session.get(QuoteRequest, request_id)
        if entity is None:
            raise AppException("Quote request not found", status_code=404)

        entity.status = payload.status
        await session.commit()
        await session.refresh(entity)
        return entity
