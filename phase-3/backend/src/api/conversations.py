"""Conversations API endpoints for managing chat history.

Provides endpoints for listing, viewing, and deleting conversations
with user authentication and ownership verification.
"""

from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user_id, get_session
from src.schemas.conversation import (
    ConversationDetail,
    ConversationListResponse,
    ConversationSummary,
    DeleteConversationResponse,
    MessageResponse,
)
from src.services.conversation_service import ConversationService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        20, ge=1, le=100, description="Items per page (max 100)"
    ),
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ConversationListResponse:
    """List user's conversations with pagination (T073, FR-029, FR-030).

    Returns conversations ordered by last_message_at DESC (most recent first).

    Args:
        page: Page number (1-indexed, default 1)
        page_size: Number of conversations per page (default 20, max 100)
        user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        Paginated list of conversation summaries

    Raises:
        401: Invalid or missing JWT token (FR-038)
        500: Database or internal error

    Example:
        ```bash
        GET /api/v1/conversations?page=1&page_size=20
        Authorization: Bearer <jwt_token>
        ```
    """
    try:
        logger.info(
            "list_conversations_request",
            user_id=str(user_id),
            page=page,
            page_size=page_size,
        )

        conversation_service = ConversationService(session)

        conversations = await conversation_service.list_conversations(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

        # Convert to response schema
        conversation_summaries = [
            ConversationSummary.model_validate(conv) for conv in conversations
        ]

        logger.info(
            "list_conversations_success",
            user_id=str(user_id),
            count=len(conversation_summaries),
        )

        return ConversationListResponse(
            conversations=conversation_summaries,
            page=page,
            page_size=page_size,
            total=len(conversation_summaries),
        )

    except Exception as e:
        logger.error(
            "list_conversations_error",
            user_id=str(user_id),
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations",
        ) from e


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ConversationDetail:
    """Get conversation details with message history (T074, FR-029, FR-030, FR-032).

    Returns full conversation metadata and all associated messages
    in chronological order.

    Args:
        conversation_id: Conversation UUID
        user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        Conversation with full message history

    Raises:
        401: Invalid or missing JWT token (FR-038)
        403: User doesn't own this conversation (FR-039)
        404: Conversation not found
        500: Database or internal error

    Example:
        ```bash
        GET /api/v1/conversations/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer <jwt_token>
        ```
    """
    try:
        logger.info(
            "get_conversation_request",
            user_id=str(user_id),
            conversation_id=str(conversation_id),
        )

        conversation_service = ConversationService(session)

        detail = await conversation_service.get_conversation_detail(
            conversation_id=conversation_id,
            user_id=user_id,
            include_messages=True,
        )

        if detail is None:
            # Either not found or unauthorized (FR-032, FR-039)
            logger.warning(
                "get_conversation_not_found_or_unauthorized",
                user_id=str(user_id),
                conversation_id=str(conversation_id),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Convert to response schema
        conversation = detail["conversation"]
        messages = detail["messages"]

        message_responses = [
            MessageResponse.model_validate(msg) for msg in messages
        ]

        logger.info(
            "get_conversation_success",
            user_id=str(user_id),
            conversation_id=str(conversation_id),
            message_count=len(message_responses),
        )

        return ConversationDetail(
            id=conversation.id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            last_message_at=conversation.last_message_at,
            messages=message_responses,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        logger.error(
            "get_conversation_error",
            user_id=str(user_id),
            conversation_id=str(conversation_id),
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation",
        ) from e


@router.delete("/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> DeleteConversationResponse:
    """Delete a conversation and all its messages (T075, FR-029, FR-030, FR-032).

    Permanently deletes the conversation and cascades to all associated messages.
    Only the conversation owner can delete it.

    Args:
        conversation_id: Conversation UUID
        user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        Deletion confirmation

    Raises:
        401: Invalid or missing JWT token (FR-038)
        403: User doesn't own this conversation (FR-039)
        404: Conversation not found
        500: Database or internal error

    Example:
        ```bash
        DELETE /api/v1/conversations/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer <jwt_token>
        ```
    """
    try:
        logger.info(
            "delete_conversation_request",
            user_id=str(user_id),
            conversation_id=str(conversation_id),
        )

        conversation_service = ConversationService(session)

        deleted = await conversation_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not deleted:
            # Either not found or unauthorized (FR-032, FR-039)
            logger.warning(
                "delete_conversation_not_found_or_unauthorized",
                user_id=str(user_id),
                conversation_id=str(conversation_id),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        logger.info(
            "delete_conversation_success",
            user_id=str(user_id),
            conversation_id=str(conversation_id),
        )

        return DeleteConversationResponse(
            success=True,
            conversation_id=conversation_id,
            message="Conversation deleted successfully",
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        logger.error(
            "delete_conversation_error",
            user_id=str(user_id),
            conversation_id=str(conversation_id),
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        ) from e
