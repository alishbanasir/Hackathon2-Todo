"""Global error handler middleware for user-friendly error responses.

Handles FastAPI exceptions and unexpected errors with appropriate HTTP status codes
and user-friendly error messages (FR-034 to FR-040).
"""

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors (400 Bad Request).

    Maps FR-040: Invalid request format, missing required fields, invalid data types.

    Args:
        request: FastAPI request object
        exc: Validation error exception

    Returns:
        JSON response with validation error details
    """
    logger.warning(
        "validation_error",
        path=request.url.path,
        method=request.method,
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "validation_error",
            "message": "Invalid request data",
            "details": exc.errors(),
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions with user-friendly messages.

    Maps:
    - FR-038: 401 Unauthorized (missing/invalid JWT token)
    - FR-039: 403 Forbidden (insufficient permissions, unauthorized conversation access)
    - FR-040: 400 Bad Request (invalid request format)

    Args:
        request: FastAPI request object
        exc: HTTP exception

    Returns:
        JSON response with error message
    """
    # Log based on severity
    if exc.status_code >= 500:
        logger.error(
            "http_error",
            status_code=exc.status_code,
            path=request.url.path,
            method=request.method,
            detail=exc.detail,
        )
    else:
        logger.info(
            "http_error",
            status_code=exc.status_code,
            path=request.url.path,
            method=request.method,
            detail=exc.detail,
        )

    # Map status codes to user-friendly error types
    error_type_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        429: "rate_limit_exceeded",
        500: "internal_server_error",
        503: "service_unavailable",
    }

    error_type = error_type_map.get(exc.status_code, "unknown_error")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_type,
            "message": exc.detail,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with generic error message.

    Maps FR-034, FR-035, FR-036:
    - Database errors → 500 Internal Server Error
    - OpenAI API failures → 500 Internal Server Error (after retries)
    - Unexpected errors → 500 Internal Server Error

    Args:
        request: FastAPI request object
        exc: Any unhandled exception

    Returns:
        JSON response with generic error message
    """
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )

    # Never expose internal error details to users
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )
