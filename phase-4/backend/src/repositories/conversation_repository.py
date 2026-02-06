"""Conversation repository for data access operations.

Handles CRUD operations for conversations with user isolation.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for Conversation entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize conversation repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session)

    async def create(self, entity: Conversation) -> Conversation:
        """Create a new conversation.

        Args:
            entity: Conversation instance to create

        Returns:
            Created conversation with generated ID

        Raises:
            IntegrityError: If openai_thread_id already exists
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[Conversation]:
        """Retrieve conversation by ID.

        Args:
            entity_id: Conversation UUID

        Returns:
            Conversation if found, None otherwise
        """
        stmt = select(Conversation).where(Conversation.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Conversation]:
        """List conversations for a user, ordered by last activity.

        Args:
            user_id: User UUID to filter by
            limit: Maximum number of conversations to return (default 20, max 100)
            offset: Number of conversations to skip for pagination

        Returns:
            List of conversations ordered by last_message_at DESC
        """
        # Enforce max limit of 100
        limit = min(limit, 100)

        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.last_message_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_last_message_at(
        self,
        conversation_id: UUID,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Update last_message_at timestamp for a conversation.

        Args:
            conversation_id: Conversation UUID
            timestamp: Timestamp to set (defaults to current UTC time)

        Returns:
            True if updated, False if conversation not found
        """
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False

        conversation.last_message_at = timestamp or datetime.utcnow()
        await self.session.flush()
        return True

    async def delete(self, entity_id: UUID) -> bool:
        """Delete conversation by ID.

        Cascades to delete all messages in the conversation.

        Args:
            entity_id: Conversation UUID

        Returns:
            True if deleted, False if not found
        """
        conversation = await self.get_by_id(entity_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.flush()
        return True

    async def get_by_thread_id(self, thread_id: str) -> Optional[Conversation]:
        """Retrieve conversation by OpenAI thread ID.

        Args:
            thread_id: OpenAI Assistants API thread ID

        Returns:
            Conversation if found, None otherwise
        """
        stmt = select(Conversation).where(Conversation.openai_thread_id == thread_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def verify_ownership(self, conversation_id: UUID, user_id: UUID) -> bool:
        """Verify that a conversation belongs to a user.

        Args:
            conversation_id: Conversation UUID
            user_id: User UUID

        Returns:
            True if user owns the conversation, False otherwise
        """
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
