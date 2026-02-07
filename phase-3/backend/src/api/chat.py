"""Chat API endpoint for AI assistant interactions.

Provides POST /api/v1/chat endpoint for natural language todo management.
"""

from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ YAHAN CHANGE - Relative import
from ..ai.gemini_client import GeminiClient
from src.api.deps import get_current_user_id, get_session
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Chat message processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "message": "I've added 'buy groceries' to your todo list.",
                        "user_message_id": "456e7890-e89b-12d3-a456-426614174111",
                        "assistant_message_id": "789e0123-e89b-12d3-a456-426614174222",
                        "processing_time_ms": 1450.25,
                    }
                }
            },
        },
        400: {
            "description": "Invalid request (message too long, invalid format)",
        },
        401: {
            "description": "Invalid or missing JWT token",
        },
        403: {
            "description": "Unauthorized conversation access (not owned by user)",
        },
        500: {
            "description": "Internal server error (OpenAI API failure, database error)",
        },
    },
    summary="Send chat message to AI assistant",
    description="""
    Process a natural language message through the AI assistant for todo management.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Features**:
    - Create todos: "remind me to buy groceries"
    - Natural language understanding via Google Gemini
    - Conversation context preservation (specify conversation_id)
    - Tool execution for todo operations

    **User Isolation**: All operations automatically filtered by authenticated user ID.

    **Rate Limits**: 60 requests per minute per user (enforced by middleware).
    """,
    tags=["chat"],
)
async def chat(
    request: ChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """Process chat message through AI assistant (FR-014, FR-015).

    Args:
        request: Chat request with message and optional conversation_id
        user_id: Authenticated user ID from JWT (injected by dependency)
        session: Database session (injected by dependency)

    Returns:
        ChatResponse with assistant's message and conversation details

    Raises:
        HTTPException 400: Invalid request (message validation failed, FR-040)
        HTTPException 401: Invalid JWT token (handled by middleware, FR-038)
        HTTPException 403: Unauthorized conversation access (FR-039)
        HTTPException 500: Internal server error (FR-034, FR-035, FR-036)
    """
    try:
        # Validate message length (1-2000 chars, FR-037)
        # Already handled by Pydantic Field validation in ChatRequest
        message_content = request.message.strip()

        if not message_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty",
            )

        # Extract conversation_id if provided (FR-019)
        conversation_id: Optional[UUID] = request.conversation_id

        logger.info(
            "chat_request_received",
            user_id=str(user_id),
            conversation_id=str(conversation_id) if conversation_id else None,
            message_length=len(message_content),
        )

        # Initialize Gemini client and ChatService
        gemini_client = GeminiClient()
        chat_service = ChatService(
            session=session,
            gemini_client=gemini_client,
        )

        # Process message (FR-016, FR-017, FR-021)
        result = await chat_service.process_message(
            message_content=message_content,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        # Return response (FR-021)
        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=result["message"],
            user_message_id=result["user_message_id"],
            assistant_message_id=result["assistant_message_id"],
            processing_time_ms=result["processing_time_ms"],
        )

    except ValueError as e:
        # Validation or authorization errors (FR-039, FR-040)
        error_message = str(e)

        if "Unauthorized" in error_message or "does not belong to user" in error_message:
            logger.warning(
                "unauthorized_conversation_access",
                user_id=str(user_id),
                conversation_id=str(conversation_id) if conversation_id else None,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation",
            )
        elif "not found" in error_message:
            logger.warning(
                "conversation_not_found",
                user_id=str(user_id),
                conversation_id=str(conversation_id) if conversation_id else None,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        else:
            logger.warning(
                "chat_validation_error",
                user_id=str(user_id),
                error=error_message,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message,
            )

    except Exception as e:
        # Internal errors: OpenAI API, database, unexpected (FR-034, FR-035, FR-036)
        logger.error(
            "chat_request_failed",
            user_id=str(user_id),
            conversation_id=str(conversation_id) if conversation_id else None,
            error=str(e),
            exc_info=True,
        )

        # Never expose internal error details to users
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message. Please try again.",
        )


# Alias endpoint for /chat/chat (handles doubled path from frontend URL misconfiguration)
@router.post("/chat/chat", include_in_schema=False)
async def chat_alias(
    request: ChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """Alias for /chat endpoint - handles doubled path."""
    return await chat(request, user_id, session)