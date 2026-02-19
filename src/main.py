from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import (
    auth_router,
    companies_router,
    driver_cash_handovers_router,
    drivers_router,
    employee_salaries_router,
    health_router,
    invoices_router,
    public_router,
    trips_router,
)
from src.core.audit import AuditLogger
from src.core.auth_protection import AuthAttemptGuard
from src.core.config import get_settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging, logger
from src.core.middleware import register_middlewares
from src.core.request_limits import RequestRateLimiter
from src.db.session import SessionFactory
from src.services.signature_encryption_integrity import check_signature_encryption_integrity


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("application_startup")
    if settings.signature_startup_integrity_check_enabled:
        async with SessionFactory() as session:
            report = await check_signature_encryption_integrity(session)
        if report.invalid_total:
            message = (
                "signature_encryption_integrity_invalid "
                f"checked_total={report.checked_total} invalid_total={report.invalid_total} "
                f"invalid_signatories={report.invalid_signatories} "
                f"invalid_invoices={report.invalid_invoices} "
                f"samples={report.sample_errors}"
            )
            if settings.signature_startup_integrity_fail_on_invalid:
                raise RuntimeError(message)
            logger.warning(message)
        else:
            logger.info(
                "signature_encryption_integrity_ok checked_total=%s",
                report.checked_total,
            )
    yield
    redis_client = getattr(app.state, "redis_client", None)
    if redis_client is not None:
        await redis_client.aclose()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    redis_client = None
    if settings.rate_limit_backend == "redis":
        try:
            from redis import asyncio as redis
        except Exception as exc:  # pragma: no cover - depends on deployment extras
            raise ValueError(
                "Redis backend requested but redis package is unavailable. Install 'redis'."
            ) from exc
        if not settings.redis_url.strip():
            raise ValueError("REDIS_URL is required when RATE_LIMIT_BACKEND=redis.")
        redis_client = redis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url, decode_responses=False
        )
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.redis_client = redis_client
    app.state.auth_attempt_guard = AuthAttemptGuard.from_settings(settings, redis_client)
    app.state.request_rate_limiter = RequestRateLimiter.from_settings(settings, redis_client)
    app.state.audit_logger = AuditLogger.from_settings(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-CSRF-Token",
            "X-Transport-Company-UUID",
            "X-Transport-Company-ID",
            "X-Step-Up-Token",
        ],
        expose_headers=["Content-Disposition"],
    )

    register_exception_handlers(app)
    register_middlewares(app)

    app.include_router(health_router)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(companies_router, prefix=settings.api_v1_prefix)
    app.include_router(drivers_router, prefix=settings.api_v1_prefix)
    app.include_router(driver_cash_handovers_router, prefix=settings.api_v1_prefix)
    app.include_router(employee_salaries_router, prefix=settings.api_v1_prefix)
    app.include_router(trips_router, prefix=settings.api_v1_prefix)
    app.include_router(invoices_router, prefix=settings.api_v1_prefix)
    app.include_router(public_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
