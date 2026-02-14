from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class GenericDBHandler(Generic[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model

    async def get(self, session: AsyncSession, entity_id: int) -> ModelT | None:
        stmt: Select[tuple[ModelT]] = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, session: AsyncSession) -> list[ModelT]:
        stmt: Select[tuple[ModelT]] = select(self.model)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, data: dict[str, Any]) -> ModelT:
        entity = self.model(**data)
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def update(
        self,
        session: AsyncSession,
        entity: ModelT,
        data: dict[str, Any],
    ) -> ModelT:
        for key, value in data.items():
            setattr(entity, key, value)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def delete(self, session: AsyncSession, entity_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        await session.execute(stmt)
        await session.commit()

    async def upsert(
        self,
        session: AsyncSession,
        values: dict[str, Any],
        conflict_columns: Sequence[str],
        update_columns: Sequence[str] | None = None,
    ) -> ModelT:
        filter_kwargs = {column: values[column] for column in conflict_columns}
        result = await session.execute(select(self.model).filter_by(**filter_kwargs))
        entity = result.scalar_one_or_none()
        if entity is None:
            return await self.create(session, values)

        updates = {
            column: values[column]
            for column in (update_columns or values.keys())
            if column in values and column not in conflict_columns
        }
        return await self.update(session, entity, updates)
