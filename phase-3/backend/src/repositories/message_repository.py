"""Message repository for chat history data access.

Handles CRUD operations for messages with efficient conversation history retrieval.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import Message
from src.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize message repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session)

    async def create(self, entity: Message) -> Message:
        """Create a new message.

        Args:
            entity: Message instance to create

        Returns:
            Created message with generated ID and timestamp
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[Message]:
        """Retrieve message by ID.

        Args:
            entity_id: Message UUID

        Returns:
            Message if found, None otherwise
        """
        stmt = select(Message).where(Message.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --- YE FUNCTION ADD KIYA HAI TAAKE ERROR KHATAM HO JAYE ---
    async def get_by_conversation_id(
        self,
        conversation_id: UUID,
        limit: Optional[int] = 50,
        offset: int = 0,
    ) -> List[Message]:
        """Alias for list_by_conversation to fix chat_service error."""
        return await self.list_by_conversation(conversation_id, limit, offset)
    # --------------------------------------------------------

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Message]:
        """List messages for a conversation in chronological order.

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return (None for all)
            offset: Number of messages to skip

        Returns:
            List of messages ordered by created_at ASC (oldest first)
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_messages(
        self,
        conversation_id: UUID,
        count: int = 20,
    ) -> List[Message]:
        """Get most recent messages for a conversation.

        Retrieves last N messages in reverse chronological order,
        then reverses the list to return chronological order.

        Args:
            conversation_id: Conversation UUID
            count: Number of recent messages to retrieve (default 20)

        Returns:
            List of recent messages in chronological order (oldest to newest)
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(count)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())

        # Reverse to get chronological order (oldest first)
        return list(reversed(messages))

    async def delete(self, entity_id: UUID) -> bool:
        """Delete message by ID.

        Args:
            entity_id: Message UUID

        Returns:
            True if deleted, False if not found
        """
        message = await self.get_by_id(entity_id)
        if not message:
            return False

        await self.session.delete(message)
        await self.session.flush()
        return True

    async def count_by_conversation(self, conversation_id: UUID) -> int:
        """Count total messages in a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Total number of messages
        """
        stmt = select(Message).where(Message.conversation_id == conversation_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())