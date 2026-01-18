"""Logging middleware using structlog for JSON-formatted request/response logs."""

import time
from typing import Callable
from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses with structured logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response with timing and status.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with logging side effects
        """
        request_id = str(uuid4())
        start_time = time.time()

        # Log incoming request (wrapped in try-except to prevent logging failures from breaking requests)
        try:
            logger.info(
                "request_started",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                client_host=request.client.host if request.client else None,
            )
        except Exception:
            pass  # Don't let logging failures break requests

        try:
            # Process request
            response = await call_next(request)

            # Calculate request duration
            duration_ms = (time.time() - start_time) * 1000

            # Log successful response
            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate request duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                exc_info=True,
            )

            # Re-raise exception to be handled by error handler
            raise
