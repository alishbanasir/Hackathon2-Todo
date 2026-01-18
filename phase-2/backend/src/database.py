"""Database connection and session management."""

import ssl
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.config import settings

# Convert postgresql:// to postgresql+asyncpg:// for async support
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Remove sslmode from URL - asyncpg doesn't support it as URL param
# SSL is handled via connect_args instead
import re
database_url = re.sub(r'[?&]sslmode=[^&]*', '', database_url)
# Clean up any trailing ? or &&
database_url = database_url.rstrip('?').replace('&&', '&').rstrip('&')

print(f"[DATABASE] Connecting to: {database_url[:50]}...")

# Create SSL context for asyncpg (Neon requires SSL)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create async engine with SSL support
try:
    engine: AsyncEngine = create_async_engine(
        database_url,
        echo=settings.is_development,
        future=True,
        connect_args={"ssl": ssl_context},
    )
    print("[DATABASE] Engine created successfully")
except Exception as e:
    print(f"[DATABASE] ERROR creating engine: {e}")
    raise

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables (for development only)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    try:
        async with async_session_maker() as session:
            yield session
    except Exception as e:
        print(f"[DATABASE] Session error: {e}")
        raise
