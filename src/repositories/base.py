"""Base repository interface for data access patterns.

Defines abstract CRUD operations that all repositories should implement.
Enables consistent data access layer and easy mocking for tests.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

# Generic type for model entities
T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with common CRUD operations.

    Subclasses must implement these methods for their specific entity type.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity in the database.

        Args:
            entity: Entity instance to create

        Returns:
            Created entity with generated ID and timestamps

        Raises:
            IntegrityError: If unique constraints are violated
            DatabaseError: If database operation fails
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Retrieve entity by ID.

        Args:
            entity_id: UUID of the entity to retrieve

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID.

        Args:
            entity_id: UUID of the entity to delete

        Returns:
            True if entity was deleted, False if not found
        """
        pass

    async def commit(self) -> None:
        """Commit current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback current transaction."""
        await self.session.rollback()

    async def refresh(self, entity: T) -> None:
        """Refresh entity from database to get latest state.

        Args:
            entity: Entity instance to refresh
        """
        await self.session.refresh(entity)
