"""Phase 3: Todo AI Chatbot - FastAPI Application Entry Point.

Main application with CORS configuration, middleware registration,
startup/shutdown handlers, and health endpoint.
"""

import structlog
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings
from src.database import engine
from src.models import Base  # Pure SQLAlchemy Base
from src.middleware.error_handler import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from src.middleware.logging import RequestLoggingMiddleware

# Configure structured logging
import logging

# Map string log level to logging constant
_log_level_map = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
_log_level = _log_level_map.get(settings.log_level.lower(), logging.INFO)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if settings.app_env == "production"
        else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(_log_level),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Todo AI Chatbot API",
    description="Phase 3: AI-powered chatbot for natural language todo management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware
from src.middleware.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.on_event("startup")
async def startup_event() -> None:
    """Execute startup tasks."""
    logger.info(
        "application_startup",
        app_env=settings.app_env,
        cors_origins=settings.cors_origins_list,
    )

    # --- DATABASE TABLES AUTO-CREATION ---
    try:
        print("[DATABASE] Auto-creating missing tables...")
        async with engine.begin() as conn:
            # Register models to metadata (already imported via Base)
            from src.models import User, Conversation, Message  # noqa: F401

            # Sync tables with Neon using pure SQLAlchemy Base
            await conn.run_sync(Base.metadata.create_all)
        print("[DATABASE] Tables created/verified successfully.")
    except Exception as e:
        print(f"[DATABASE ERROR] Could not create tables: {e}")
    # -------------------------------------

    # Validate critical configuration
    required_settings = [
        ("DATABASE_URL", settings.database_url),
        ("GOOGLE_API_KEY", settings.google_api_key),
        ("BETTER_AUTH_SECRET", settings.better_auth_secret),
    ]

    missing = [name for name, value in required_settings if not value]
    if missing:
        logger.error("missing_required_settings", missing=missing)
        raise RuntimeError(f"Missing required settings: {', '.join(missing)}")

    logger.info("application_ready")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute shutdown tasks."""
    logger.info("application_shutdown")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> JSONResponse:
    from datetime import datetime, timezone
    gemini_configured = bool(settings.google_api_key)
    database_configured = bool(settings.database_url)
    overall_status = "healthy" if (gemini_configured and database_configured) else "degraded"

    return JSONResponse(
        content={
            "status": overall_status,
            "phase": "3",
            "service": "todo-ai-chatbot",
            "gemini_configured": gemini_configured,
            "database_configured": database_configured,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "name": "Todo AI Chatbot API",
            "version": "1.0.0",
            "phase": "3",
            "docs": "/docs",
        }
    )


@app.get("/ping")
async def ping():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("pong")


# Import and register API routers
from src.api import chat, conversations

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(conversations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower(),
    )