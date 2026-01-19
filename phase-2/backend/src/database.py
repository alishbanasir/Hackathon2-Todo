"""Database connection and session management - Unified for Phase 2 & 3."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from src.config import settings

# Convert postgresql:// to postgresql+asyncpg:// for async support
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=settings.is_development,
    future=True,
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Phase 2 uses 'get_session'
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for Phase 2 async database session."""
    async with async_session_maker() as session:
        yield session

# Phase 3 uses 'get_db_session' 
# Hum bas Phase 2 wale function ko hi naye naam se point kar rahe hain
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for Phase 3 (AI Assistant) database session."""
    async with async_session_maker() as session:
        yield session