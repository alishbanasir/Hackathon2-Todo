"""Conversation service for managing chat history and context.

Provides high-level conversation operations with user isolation and pagination.
"""

from typing import List, Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message
from src.repositories.conversation_repository import ConversationRepository
from src.repositories.message_repository import MessageRepository

logger = structlog.get_logger(__name__)


class ConversationService:
    """Service for conversation management operations.

    Handles listing, retrieving, and deleting conversations with
    user ownership verification and pagination support.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize conversation service.

        Args:
            session: Database session for repository operations
        """
        self.session = session
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)

    async def list_conversations(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Conversation]:
        """List conversations for a user with pagination (T069, FR-032).

        Args:
            user_id: User ID to filter conversations by
            page: Page number (1-indexed, default 1)
            page_size: Number of conversations per page (default 20, max 100)

        Returns:
            List of conversations ordered by last_message_at DESC
        """
        # Enforce max page size of 100
        page_size = min(page_size, 100)

        # Ensure positive page number
        page = max(page, 1)

        # Calculate offset
        offset = (page - 1) * page_size

        logger.info(
            "listing_conversations",
            user_id=str(user_id),
            page=page,
            page_size=page_size,
            offset=offset,
        )

        conversations = await self.conversation_repo.list_by_user(
            user_id=user_id,
            limit=page_size,
            offset=offset,
        )

        logger.info(
            "conversations_listed",
            user_id=str(user_id),
            count=len(conversations),
        )

        return conversations

    async def get_conversation_detail(
        self,
        conversation_id: UUID,
        user_id: UUID,
        include_messages: bool = True,
        message_limit: Optional[int] = None,
    ) -> Optional[dict]:
        """Get conversation details with optional message history (T074, FR-032).

        Args:
            conversation_id: Conversation UUID
            user_id: User ID for ownership verification
            include_messages: Whether to include message history (default True)
            message_limit: Maximum number of messages to include (None for all)

        Returns:
            Dictionary with conversation and messages, or None if not found/unauthorized
        """
        logger.info(
            "getting_conversation_detail",
            conversation_id=str(conversation_id),
            user_id=str(user_id),
            include_messages=include_messages,
        )

        # Verify ownership (FR-032)
        has_access = await self.conversation_repo.verify_ownership(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not has_access:
            logger.warning(
                "conversation_access_denied",
                conversation_id=str(conversation_id),
                user_id=str(user_id),
            )
            return None

        # Get conversation
        conversation = await self.conversation_repo.get_by_id(conversation_id)

        if not conversation:
            logger.warning(
                "conversation_not_found",
                conversation_id=str(conversation_id),
            )
            return None

        # Build response
        result = {
            "conversation": conversation,
            "messages": [],
        }

        # Include messages if requested
        if include_messages:
            messages = await self.message_repo.list_by_conversation(
                conversation_id=conversation_id,
                limit=message_limit,
            )
            result["messages"] = messages

            logger.info(
                "conversation_detail_retrieved",
                conversation_id=str(conversation_id),
                message_count=len(messages),
            )

        return result

    async def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a conversation with ownership verification (T075, FR-032).

        Cascades to delete all messages in the conversation.

        Args:
            conversation_id: Conversation UUID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found or unauthorized
        """
        logger.info(
            "deleting_conversation",
            conversation_id=str(conversation_id),
            user_id=str(user_id),
        )

        # Verify ownership (FR-032)
        has_access = await self.conversation_repo.verify_ownership(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not has_access:
            logger.warning(
                "conversation_delete_denied",
                conversation_id=str(conversation_id),
                user_id=str(user_id),
            )
            return False

        # Delete conversation (cascades to messages)
        deleted = await self.conversation_repo.delete(conversation_id)

        if deleted:
            await self.session.commit()
            logger.info(
                "conversation_deleted",
                conversation_id=str(conversation_id),
            )
        else:
            logger.warning(
                "conversation_delete_failed",
                conversation_id=str(conversation_id),
            )

        return deleted

    async def get_conversation_context(
        self,
        conversation_id: UUID,
        user_id: UUID,
        message_count: int = 20,
    ) -> Optional[List[Message]]:
        """Get recent messages for context window (T071).

        Retrieves the last N messages from a conversation for
        OpenAI context window management.

        Args:
            conversation_id: Conversation UUID
            user_id: User ID for ownership verification
            message_count: Number of recent messages to retrieve (default 20)

        Returns:
            List of recent messages in chronological order, or None if unauthorized
        """
        logger.info(
            "getting_conversation_context",
            conversation_id=str(conversation_id),
            user_id=str(user_id),
            message_count=message_count,
        )

        # Verify ownership (FR-032)
        has_access = await self.conversation_repo.verify_ownership(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not has_access:
            logger.warning(
                "conversation_context_denied",
                conversation_id=str(conversation_id),
                user_id=str(user_id),
            )
            return None

        # Get recent messages
        messages = await self.message_repo.get_recent_messages(
            conversation_id=conversation_id,
            count=message_count,
        )

        logger.info(
            "conversation_context_retrieved",
            conversation_id=str(conversation_id),
            message_count=len(messages),
        )

        return messages
