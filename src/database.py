"""Database connection and session management.

Provides async database engine and session maker for PostgreSQL connections.
Reuses the same Neon database from Phase 2 with extended schema for Phase 3.
"""

import re
import ssl
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

# Import Base and all models to register them with SQLAlchemy metadata
# This must happen before any database operations
from src.models import Base, User, Conversation, Message  # noqa: F401

# Prepare database URL for asyncpg
database_url = settings.database_url

# Remove sslmode from URL - asyncpg doesn't support it as URL param
# SSL is handled via connect_args instead
database_url = re.sub(r'[?&]sslmode=[^&]*', '', database_url)
# Clean up any trailing ? or &&
database_url = database_url.rstrip('?').replace('&&', '&').rstrip('&')

print(f"[DATABASE] Connecting to: {database_url[:50]}...")

# Create SSL context for asyncpg (Neon requires SSL)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create async engine with connection pooling and SSL
engine = create_async_engine(
    database_url,
    echo=settings.app_env == "development",  # Log SQL in development
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={"ssl": ssl_context},
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session injection.

    Yields:
        AsyncSession: Database session for the request lifecycle.

    Example:
        ```python
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_db_tables() -> None:
    """Create all database tables.

    NOTE: In production, use Alembic migrations instead of this function.
    This is provided for testing and development convenience only.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_tables() -> None:
    """Drop all database tables.

    WARNING: This will delete all data. Only use for testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
