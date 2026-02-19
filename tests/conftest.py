from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.auth import hash_password
from src.core.config import get_settings
from src.db.base import Base
from src.db.session import get_db_session
from src.main import create_app
from src.models.admin_user import AdminUser
from src.models.transport_company import TransportCompany

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.fixture
async def app() -> AsyncIterator[FastAPI]:
    engine = create_async_engine(TEST_DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as seed_session:
        transport_company = TransportCompany(
            uuid="00000000-0000-0000-0000-000000000001",
            name="Test Transport Company",
            email="test@transport.local",
            location="Test City",
            trn="TRNTEST001",
        )
        seed_session.add(transport_company)
        await seed_session.flush()
        seed_session.add(
            AdminUser(
                username="admin",
                password_hash=hash_password("secret"),
                transport_company_id=transport_company.id,
            )
        )
        second_transport_company = TransportCompany(
            uuid="00000000-0000-0000-0000-000000000002",
            name="Second Transport Company",
            email="test2@transport.local",
            location="Second City",
            trn="TRNTEST002",
        )
        seed_session.add(second_transport_company)
        await seed_session.flush()
        seed_session.add(
            AdminUser(
                username="admin2",
                password_hash=hash_password("secret"),
                transport_company_id=second_transport_company.id,
            )
        )
        await seed_session.commit()

    async def override_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    test_app = create_app()
    test_app.dependency_overrides[get_db_session] = override_session

    yield test_app

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client
