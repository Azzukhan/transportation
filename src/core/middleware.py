import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from src.core.config import Settings
from src.core.exceptions import error_payload
from src.core.logging import logger
from src.core.request_limits import RequestRateLimiter


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_complete method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


async def security_headers_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        return response

    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", settings.security_referrer_policy)
    if settings.security_csp:
        response.headers.setdefault("Content-Security-Policy", settings.security_csp)
    if settings.is_production:
        response.headers.setdefault(
            "Strict-Transport-Security", settings.strict_transport_security_value
        )
    return response


async def csrf_protection_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        return await call_next(request)

    if request.method.upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
        return await call_next(request)

    path = request.url.path
    api_prefix = settings.api_v1_prefix.rstrip("/")
    if not path.startswith(api_prefix):
        return await call_next(request)
    if path.startswith(f"{api_prefix}/public/"):
        return await call_next(request)
    if path == f"{api_prefix}/auth/token":
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if auth_header:
        return await call_next(request)

    has_auth_cookie = bool(
        request.cookies.get(settings.auth_access_cookie_name)
        or request.cookies.get(settings.auth_refresh_cookie_name)
    )
    if not has_auth_cookie:
        return await call_next(request)

    csrf_cookie = request.cookies.get(settings.auth_csrf_cookie_name)
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        return JSONResponse(
            status_code=403,
            content=error_payload(
                request=request,
                message="Invalid CSRF token",
                code="csrf_invalid",
            ),
        )
    return await call_next(request)


def _resolve_body_limit(*, settings: Settings, path: str, method: str) -> int:
    upper_method = method.upper()
    if upper_method not in {"POST", "PUT", "PATCH"}:
        return settings.max_request_body_bytes
    if path.endswith("/auth/token") or path.endswith("/auth/token/refresh"):
        return settings.max_auth_body_bytes
    if path.startswith(f"{settings.api_v1_prefix.rstrip('/')}/public/"):
        return settings.max_public_request_body_bytes
    if path.endswith("/employee-salaries/import") or "/invoices/signatories" in path:
        return settings.max_upload_body_bytes
    return settings.max_request_body_bytes


def _too_large_response(request: Request, limit_bytes: int) -> JSONResponse:
    return JSONResponse(
        status_code=413,
        content=error_payload(
            request=request,
            message=f"Request payload too large. Limit is {limit_bytes} bytes.",
            code="payload_too_large",
        ),
    )


async def request_protection_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    settings = request.app.state.settings
    rate_limiter = request.app.state.request_rate_limiter
    if not isinstance(settings, Settings) or not isinstance(rate_limiter, RequestRateLimiter):
        return await call_next(request)

    path = request.url.path
    if path.startswith(settings.api_v1_prefix.rstrip("/")):
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        client_ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for.strip()
            else (request.client.host if request.client else "unknown")
        )
        decision = await rate_limiter.check(client_id=client_ip, path=path, method=request.method)
        if not decision.allowed:
            retry_after = decision.retry_after_seconds or 1
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content=error_payload(
                    request=request,
                    message=f"Rate limit exceeded for scope '{decision.scope}'. Try again in {retry_after} seconds.",
                    code="rate_limited",
                ),
            )

    limit_bytes = _resolve_body_limit(settings=settings, path=path, method=request.method)
    if request.method.upper() in {"POST", "PUT", "PATCH"} and limit_bytes > 0:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > limit_bytes:
                    return _too_large_response(request, limit_bytes)
            except ValueError:
                pass
        else:
            body = await request.body()
            if len(body) > limit_bytes:
                return _too_large_response(request, limit_bytes)

            async def receive() -> dict[str, object]:
                return {
                    "type": "http.request",
                    "body": body,
                    "more_body": False,
                }

            request._receive = receive

    return await call_next(request)


def register_middlewares(app: FastAPI) -> None:
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(security_headers_middleware)
    app.middleware("http")(csrf_protection_middleware)
    app.middleware("http")(request_protection_middleware)
