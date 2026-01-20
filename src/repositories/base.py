"""Abstract repository interface for clean architecture."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar
from uuid import UUID

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Abstract repository interface.

    This interface enables the repository pattern, allowing business logic
    to remain independent of the specific database implementation.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity in the database.

        Args:
            entity: The entity to create

        Returns:
            The created entity with generated ID and timestamps
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The entity's unique identifier

        Returns:
            The entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity.

        Args:
            entity: The entity with updated values

        Returns:
            The updated entity
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its ID.

        Args:
            entity_id: The entity's unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass
