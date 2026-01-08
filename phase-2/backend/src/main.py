"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth, todos
from src.config import settings
from src.middleware.logging import LoggingMiddleware

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="Phase II Todo Full-Stack Web Application - Backend API",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add structured logging middleware
app.add_middleware(LoggingMiddleware)

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(todos.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dictionary with status message.
    """
    return {"status": "healthy", "service": "todo-api"}


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message with API info.
    """
    return {
        "message": "Todo API - Phase II",
        "version": "0.1.0",
        "docs": "/docs" if settings.is_development else "disabled",
    }
