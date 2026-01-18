"""Conversation model for tracking chat sessions.

Each conversation represents a unique chat session between a user and the AI assistant,
mapped to an OpenAI thread for context preservation.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation entity for AI chat sessions.

    Maps to OpenAI Assistants API threads for context management.
    One user can have multiple conversations (different topics/contexts).
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        description="Unique conversation identifier",
    )

    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        description="User who owns this conversation (FK to Phase 2 users table)",
    )

    # FIXED: Removed unique=True to allow multiple empty threads during testing
    openai_thread_id: str = Field(
        sa_column=Column(
            String(255),
            nullable=True, # Changed to True
            unique=False,  # Changed to False
        ),
        default="",
        description="OpenAI thread ID for context management",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
        description="Conversation creation timestamp",
    )

    last_message_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            index=True,
        ),
        description="Timestamp of last message in conversation",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43d7-9012-345678901234",
                "openai_thread_id": "thread_abc123xyz789",
                "created_at": "2026-01-12T10:30:00Z",
                "last_message_at": "2026-01-12T15:45:00Z",
            }
        }