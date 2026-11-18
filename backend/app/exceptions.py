import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base exception for expected application failures."""

    def __init__(
        self,
        status_code: int,
        code: str,
        detail: str,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail
        self.headers = dict(headers or {})


class BadRequestError(AppError):
    def __init__(self, detail: str = "Invalid request", code: str = "bad_request") -> None:
        super().__init__(400, code, detail)


class UnauthorizedError(AppError):
    def __init__(
        self,
        detail: str = "Authentication is required",
        code: str = "unauthorized",
    ) -> None:
        super().__init__(401, code, detail, {"WWW-Authenticate": "Bearer"})


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Access is forbidden", code: str = "forbidden") -> None:
        super().__init__(403, code, detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Resource not found", code: str = "not_found") -> None:
        super().__init__(404, code, detail)


class ConflictError(AppError):
    def __init__(self, detail: str = "Resource conflict", code: str = "conflict") -> None:
        super().__init__(409, code, detail)


class RateLimitError(AppError):
    def __init__(
        self,
        retry_after: int,
        detail: str = "Too many attempts. Try again shortly.",
        code: str = "rate_limited",
    ) -> None:
        super().__init__(429, code, detail, {"Retry-After": str(retry_after)})


def error_response(
    status_code: int,
    code: str,
    detail: Any,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    response_headers = {"Cache-Control": "no-store"}
    response_headers.update(headers or {})
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "code": code},
        headers=response_headers,
    )


def http_error_code(status_code: int) -> str:
    return {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        429: "rate_limited",
    }.get(status_code, "http_error")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, error: AppError):
        return error_response(
            error.status_code,
            error.code,
            error.detail,
            error.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, error: RequestValidationError):
        # Pydantic's default output may echo passwords and other submitted values.
        details = [
            {"loc": item["loc"], "msg": item["msg"], "type": item["type"]}
            for item in error.errors()
        ]
        return error_response(422, "validation_error", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_request: Request, error: StarletteHTTPException):
        return error_response(
            error.status_code,
            http_error_code(error.status_code),
            error.detail,
            error.headers,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, error: SQLAlchemyError):
        logger.error(
            "Unhandled database error during %s %s",
            request.method,
            request.url.path,
            exc_info=(type(error), error, error.__traceback__),
        )
        return error_response(
            500,
            "database_error",
            "The request could not be completed",
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, error: Exception):
        logger.error(
            "Unhandled application error during %s %s",
            request.method,
            request.url.path,
            exc_info=(type(error), error, error.__traceback__),
        )
        return error_response(
            500,
            "internal_error",
            "The request could not be completed",
        )
