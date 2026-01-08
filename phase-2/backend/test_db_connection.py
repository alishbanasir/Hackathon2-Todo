"""Test script to verify database connection."""

import asyncio
from sqlalchemy import text

from src.database import engine


async def test_connection() -> None:
    """Test database connection."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                print(f"   Connected to: {engine.url.database}")
            else:
                print("❌ Database connection failed: unexpected result")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease check:")
        print("1. DATABASE_URL is set correctly in backend/.env")
        print("2. Neon PostgreSQL database is accessible")
        print("3. Network connectivity is working")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())
