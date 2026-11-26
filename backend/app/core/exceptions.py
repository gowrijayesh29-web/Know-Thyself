"""
Custom exceptions and exception handlers.
"""
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError

from app.schemas.base import ErrorResponse, ErrorDetail
from app.core.config import settings


class KnowThyselfException(Exception):
    """Base exception for Know Thyself application."""
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[list[ErrorDetail]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class AuthenticationError(KnowThyselfException):
    """Authentication related errors."""
    def __init__(self, message: str = "Authentication failed", details: Optional[list[ErrorDetail]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(KnowThyselfException):
    """Authorization related errors."""
    def __init__(self, message: str = "Not authorized", details: Optional[list[ErrorDetail]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundError(KnowThyselfException):
    """Resource not found errors."""
    def __init__(self, resource: str, identifier: Any, details: Optional[list[ErrorDetail]] = None):
        super().__init__(
            message=f"{resource} not found",
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details or [ErrorDetail(field="id", message=f"{resource} with id {identifier} not found")],
        )


class ValidationErrorException(KnowThyselfException):
    """Validation errors."""
    def __init__(self, message: str, details: Optional[list[ErrorDetail]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ConflictError(KnowThyselfException):
    """Resource conflict errors."""
    def __init__(self, message: str, details: Optional[list[ErrorDetail]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class RateLimitError(KnowThyselfException):
    """Rate limit exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=[ErrorDetail(field="retry_after", message=str(retry_after))],
        )


class ExternalServiceError(KnowThyselfException):
    """External service errors."""
    def __init__(self, service: str, message: str, details: Optional[list[ErrorDetail]] = None):
        super().__init__(
            message=f"{service} error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


class AIServiceError(KnowThyselfException):
    """AI service errors."""
    def __init__(self, message: str, details: Optional[list[ErrorDetail]] = None):
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


# Exception handlers
async def knowthyself_exception_handler(request: Request, exc: KnowThyselfException) -> JSONResponse:
    """Handle KnowThyselfException."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=request.headers.get("X-Request-ID"),
        ).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            code=error["type"],
        )
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message="Request validation failed",
            details=details,
            request_id=request.headers.get("X-Request-ID"),
        ).model_dump(),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy errors."""
    if isinstance(exc, IntegrityError):
        # Handle unique constraint violations
        error_msg = str(exc.orig)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponse(
                    error="CONFLICT",
                    message="A record with this value already exists",
                    details=[ErrorDetail(field="unknown", message=error_msg)],
                    request_id=request.headers.get("X-Request-ID"),
                ).model_dump(),
            )

    # Generic database error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="DATABASE_ERROR",
            message="A database error occurred" if not settings.DEBUG else str(exc),
            details=[],
            request_id=request.headers.get("X-Request-ID"),
        ).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    import logging
    logger = logging.getLogger(__name__)
    logger.exception("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An unexpected error occurred" if not settings.DEBUG else str(exc),
            details=[],
            request_id=request.headers.get("X-Request-ID"),
        ).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers."""
    app.add_exception_handler(KnowThyselfException, knowthyself_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)