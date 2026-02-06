"""Abstract repository interface for clean architecture."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Abstract repository interface.

    This interface enables the repository pattern, allowing business logic
    to remain independent of the specific database implementation.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        pass


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with session injection.

    Used by conversation and message repositories that receive
    a database session from the service layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        pass
