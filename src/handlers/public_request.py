from __future__ import annotations

from fastapi import Request
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import decode_access_token
from src.core.config import get_settings
from src.core.exceptions import AppException
from src.models.admin_user import AdminUser
from src.models.contact_request import ContactRequest
from src.models.quote_request import QuoteRequest
from src.models.transport_company import TransportCompany
from src.schemas.contact import ContactRequestCreate, ContactRequestUpdate
from src.schemas.quote import QuoteRequestCreate, QuoteRequestUpdate


class PublicRequestHandler:
    async def resolve_transport_company_id(
        self,
        session: AsyncSession,
        request: Request,
    ) -> int:
        resolved_ids: set[int] = set()

        tenant_uuid = request.headers.get("X-Transport-Company-UUID", "").strip()
        if tenant_uuid:
            stmt: Select[tuple[TransportCompany]] = select(TransportCompany).where(
                TransportCompany.uuid == tenant_uuid
            )
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            if tenant is None:
                raise AppException(
                    "Transport company not found for provided UUID",
                    status_code=404,
                    code="tenant_not_found",
                )
            resolved_ids.add(tenant.id)

        tenant_id_raw = request.headers.get("X-Transport-Company-ID", "").strip()
        if tenant_id_raw:
            try:
                tenant_id = int(tenant_id_raw)
            except ValueError as exc:
                raise AppException(
                    "X-Transport-Company-ID must be a valid integer",
                    status_code=400,
                    code="tenant_unresolved",
                ) from exc
            stmt_by_id: Select[tuple[TransportCompany]] = select(TransportCompany).where(
                TransportCompany.id == tenant_id
            )
            result_by_id = await session.execute(stmt_by_id)
            tenant_by_id = result_by_id.scalar_one_or_none()
            if tenant_by_id is None:
                raise AppException(
                    "Transport company not found for provided ID",
                    status_code=404,
                    code="tenant_not_found",
                )
            resolved_ids.add(tenant_by_id.id)

        bearer = request.headers.get("Authorization", "")
        if bearer.lower().startswith("bearer "):
            token = bearer.split(" ", 1)[1].strip()
            if token:
                subject = decode_access_token(token, get_settings()).sub
                admin_stmt: Select[tuple[AdminUser]] = select(AdminUser).where(
                    AdminUser.username == subject
                )
                admin_result = await session.execute(admin_stmt)
                admin_user = admin_result.scalar_one_or_none()
                if admin_user is not None:
                    resolved_ids.add(admin_user.transport_company_id)

        if not resolved_ids:
            raise AppException(
                "Tenant could not be resolved. Provide X-Transport-Company-UUID header, tenant ID header, or authenticated token.",
                status_code=400,
                code="tenant_unresolved",
            )
        if len(resolved_ids) > 1:
            raise AppException(
                "Conflicting tenant identifiers were provided",
                status_code=403,
                code="tenant_mismatch",
            )
        return next(iter(resolved_ids))

    async def create_contact_request(
        self,
        session: AsyncSession,
        transport_company_id: int,
        payload: ContactRequestCreate,
    ) -> ContactRequest:
        values = payload.model_dump()
        values["transport_company_id"] = transport_company_id
        entity = ContactRequest(**values)
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def list_contact_requests(
        self,
        session: AsyncSession,
        transport_company_id: int,
    ) -> list[ContactRequest]:
        stmt: Select[tuple[ContactRequest]] = (
            select(ContactRequest)
            .where(ContactRequest.transport_company_id == transport_company_id)
            .order_by(ContactRequest.created_at.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update_contact_request(
        self,
        session: AsyncSession,
        transport_company_id: int,
        request_id: int,
        payload: ContactRequestUpdate,
    ) -> ContactRequest:
        stmt: Select[tuple[ContactRequest]] = (
            select(ContactRequest)
            .where(ContactRequest.id == request_id)
            .where(ContactRequest.transport_company_id == transport_company_id)
        )
        result = await session.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppException("Contact request not found", status_code=404)

        entity.status = payload.status
        await session.commit()
        await session.refresh(entity)
        return entity

    async def create_quote_request(
        self,
        session: AsyncSession,
        transport_company_id: int,
        payload: QuoteRequestCreate,
    ) -> QuoteRequest:
        values = payload.model_dump()
        values["transport_company_id"] = transport_company_id
        entity = QuoteRequest(**values)
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def list_quote_requests(
        self,
        session: AsyncSession,
        transport_company_id: int,
    ) -> list[QuoteRequest]:
        stmt: Select[tuple[QuoteRequest]] = (
            select(QuoteRequest)
            .where(QuoteRequest.transport_company_id == transport_company_id)
            .order_by(QuoteRequest.created_at.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update_quote_request(
        self,
        session: AsyncSession,
        transport_company_id: int,
        request_id: int,
        payload: QuoteRequestUpdate,
    ) -> QuoteRequest:
        stmt: Select[tuple[QuoteRequest]] = (
            select(QuoteRequest)
            .where(QuoteRequest.id == request_id)
            .where(QuoteRequest.transport_company_id == transport_company_id)
        )
        result = await session.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppException("Quote request not found", status_code=404)

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)
        await session.commit()
        await session.refresh(entity)
        return entity
