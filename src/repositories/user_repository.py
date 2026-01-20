"""User repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.models.user import User


class UserRepository:
    """Repository for User entity data access."""

    async def create_user(self, email: str, password_hash: str) -> User:
        """Create a new user in the database.

        Args:
            email: User's email address (must be unique)
            password_hash: Argon2id hashed password

        Returns:
            Created user with generated ID and timestamp

        Raises:
            IntegrityError: If email already exists
        """
        async with async_session_maker() as session:
            user = User(email=email, password_hash=password_hash)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email address.

        Args:
            email: User's email address

        Returns:
            User if found, None otherwise
        """
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalars().first()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User if found, None otherwise
        """
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalars().first()

    async def update_password(self, email: str, password_hash: str) -> Optional[User]:
        """Update user's password by email.

        Args:
            email: User's email address
            password_hash: New Argon2id hashed password

        Returns:
            Updated user if found, None otherwise
        """
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalars().first()

            if user:
                user.password_hash = password_hash
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user

            return None
