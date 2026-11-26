"""
Logging configuration using structlog.
"""
from typing import Optional
import sys
import logging
import structlog
from typing import Any, Dict

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging."""
    # Standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(name)


# Request logging middleware helper
class RequestLogger:
    """Log HTTP requests and responses."""

    def __init__(self):
        self.logger = get_logger("request")

    async def log_request(self, request, response, duration_ms: float) -> None:
        """Log request details."""
        self.logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

    def log_error(self, request, error: Exception, duration_ms: float) -> None:
        """Log request error."""
        self.logger.error(
            "http_request_error",
            method=request.method,
            path=request.url.path,
            error_type=type(error).__name__,
            error_message=str(error),
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
        )


# Database query logging
def log_query(query: str, params: Dict[str, Any], duration_ms: float) -> None:
    """Log database query."""
    logger = get_logger("database")
    logger.debug(
        "db_query",
        query=query,
        params=params,
        duration_ms=duration_ms,
    )


# AI service logging
def log_ai_request(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: float,
    success: bool,
    error: Optional[str] = None,
) -> None:
    """Log AI service request."""
    logger = get_logger("ai")
    logger.info(
        "ai_request",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        duration_ms=duration_ms,
        success=success,
        error=error,
    )


# Business event logging
def log_business_event(
    event_type: str,
    user_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Log business events for analytics."""
    logger = get_logger("business")
    logger.info(
        "business_event",
        event_type=event_type,
        user_id=user_id,
        **kwargs,
    )