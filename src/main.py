from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import (
    auth_router,
    companies_router,
    health_router,
    invoices_router,
    public_router,
    trips_router,
)
from src.core.config import get_settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging, logger
from src.core.middleware import register_middlewares


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("application_startup")
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    register_middlewares(app)

    app.include_router(health_router)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(companies_router, prefix=settings.api_v1_prefix)
    app.include_router(trips_router, prefix=settings.api_v1_prefix)
    app.include_router(invoices_router, prefix=settings.api_v1_prefix)
    app.include_router(public_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
