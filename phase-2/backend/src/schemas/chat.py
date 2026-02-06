"""Pydantic schemas for chat API requests and responses."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint.

    Attributes:
        message: User's chat message (1-2000 characters, FR-037)
        conversation_id: Optional UUID of existing conversation (FR-019)
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's chat message",
    )

    conversation_id: Optional[UUID] = Field(
        None,
        description="Optional conversation ID to continue existing chat",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "message": "Add a task to buy groceries tomorrow",
                "conversation_id": None,
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint.

    Attributes:
        conversation_id: UUID of the conversation
        message: Assistant's response message
        user_message_id: UUID of user's saved message
        assistant_message_id: UUID of assistant's saved message
        processing_time_ms: Time taken to process the request in milliseconds
    """

    conversation_id: str = Field(
        ...,
        description="Conversation UUID",
    )

    message: str = Field(
        ...,
        description="Assistant's response message",
    )

    user_message_id: str = Field(
        ...,
        description="UUID of user's message in database",
    )

    assistant_message_id: str = Field(
        ...,
        description="UUID of assistant's message in database",
    )

    processing_time_ms: float = Field(
        ...,
        description="Processing time in milliseconds",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "I've added 'buy groceries tomorrow' to your todo list.",
                "user_message_id": "456e7890-e89b-12d3-a456-426614174111",
                "assistant_message_id": "789e0123-e89b-12d3-a456-426614174222",
                "processing_time_ms": 1450.25,
            }
        }
