"""Message model for chat history persistence.

Stores all messages (user and assistant) for audit trail and conversation history.
Messages belong to conversations and are displayed in chronological order.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message role enumeration.

    Distinguishes between user-sent messages and AI assistant responses.
    """

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message entity for chat history.

    Persists all messages in conversations for audit trail and history retrieval.
    Each message belongs to exactly one conversation and has a role (user or assistant).
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        description="Unique message identifier",
    )

    conversation_id: UUID = Field(
        sa_column=Column(
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,  # Index for efficient conversation message retrieval
        ),
        description="Conversation this message belongs to (FK to conversations table)",
    )

    role: MessageRole = Field(
        sa_column=Column(
            SQLEnum(MessageRole, name="message_role", native_enum=False),
            nullable=False,
        ),
        description="Message sender role: user or assistant",
    )

    content: str = Field(
        sa_column=Column(
            Text,
            nullable=False,
        ),
        description="Message content (text)",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            index=True,  # Index for chronological ordering
        ),
        description="Message creation timestamp",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174111",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "user",
                "content": "Add a task to buy groceries tomorrow",
                "created_at": "2026-01-12T10:30:15Z",
            }
        }
