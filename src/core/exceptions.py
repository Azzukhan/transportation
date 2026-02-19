from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.types import ExceptionHandler

from src.core.logging import logger


@dataclass(slots=True)
class AppException(Exception):
    message: str
    status_code: int = 400
    code: str = "app_error"


def error_payload(
    *,
    request: Request,
    message: str,
    code: str,
) -> dict[str, object]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
        "path": request.url.path,
        "timestamp": datetime.now(UTC).isoformat(),
    }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(
            request=request,
            message=exc.message,
            code=exc.code,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    code = "unauthorized" if exc.status_code == status.HTTP_401_UNAUTHORIZED else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(request=request, message=detail, code=code),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            **error_payload(
                request=request,
                message="Validation failed",
                code="validation_error",
            ),
            "details": exc.errors(),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception path=%s", request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload(
            request=request,
            message="Internal server error",
            code="internal_error",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AppException,
        cast(ExceptionHandler, app_exception_handler),
    )
    app.add_exception_handler(
        HTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(
        Exception,
        cast(ExceptionHandler, unhandled_exception_handler),
    )
