"""Pydantic schemas for conversation API requests and responses.

Defines data transfer objects for conversation listing, detail retrieval,
and message history.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Schema for a single message in conversation history.

    Used in conversation detail responses to show chat history.
    """

    id: UUID = Field(description="Message unique identifier")
    conversation_id: UUID = Field(description="Parent conversation ID")
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message text content")
    created_at: datetime = Field(description="Message timestamp")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "456e7890-e12b-34d5-a678-901234567890",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "user",
                "content": "Show me my tasks",
                "created_at": "2026-01-13T10:30:00Z",
            }
        }


class ConversationSummary(BaseModel):
    """Schema for conversation in list view.

    Provides minimal information for conversation listing without message history.
    """

    id: UUID = Field(description="Conversation unique identifier")
    user_id: UUID = Field(description="Owner user ID")
    created_at: datetime = Field(description="Conversation creation timestamp")
    last_message_at: datetime = Field(
        description="Timestamp of most recent message"
    )

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43d7-9012-345678901234",
                "created_at": "2026-01-12T10:30:00Z",
                "last_message_at": "2026-01-13T15:45:00Z",
            }
        }


class ConversationDetail(BaseModel):
    """Schema for detailed conversation view with message history.

    Includes full conversation metadata and all associated messages.
    """

    id: UUID = Field(description="Conversation unique identifier")
    user_id: UUID = Field(description="Owner user ID")
    created_at: datetime = Field(description="Conversation creation timestamp")
    last_message_at: datetime = Field(
        description="Timestamp of most recent message"
    )
    messages: List[MessageResponse] = Field(
        description="Conversation message history in chronological order",
        default_factory=list,
    )

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43d7-9012-345678901234",
                "created_at": "2026-01-12T10:30:00Z",
                "last_message_at": "2026-01-13T15:45:00Z",
                "messages": [
                    {
                        "id": "456e7890-e12b-34d5-a678-901234567890",
                        "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "role": "user",
                        "content": "Show me my tasks",
                        "created_at": "2026-01-13T10:30:00Z",
                    },
                    {
                        "id": "567f8901-f23c-45e6-b789-012345678901",
                        "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "role": "assistant",
                        "content": "You have 3 tasks: 2 pending and 1 completed.",
                        "created_at": "2026-01-13T10:30:02Z",
                    },
                ],
            }
        }


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list response.

    Includes pagination metadata and conversation summaries.
    """

    conversations: List[ConversationSummary] = Field(
        description="List of conversation summaries"
    )
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    total: int = Field(description="Total number of conversations (on current page)")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "conversations": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "987fcdeb-51a2-43d7-9012-345678901234",
                        "created_at": "2026-01-12T10:30:00Z",
                        "last_message_at": "2026-01-13T15:45:00Z",
                    }
                ],
                "page": 1,
                "page_size": 20,
                "total": 1,
            }
        }


class DeleteConversationResponse(BaseModel):
    """Schema for conversation deletion response.

    Confirms successful deletion.
    """

    success: bool = Field(description="Whether deletion succeeded")
    conversation_id: UUID = Field(description="Deleted conversation ID")
    message: str = Field(description="Human-readable confirmation message")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "success": True,
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "Conversation deleted successfully",
            }
        }
