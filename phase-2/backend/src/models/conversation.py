"""Conversation model for tracking chat sessions.

Each conversation represents a unique chat session between a user and the AI assistant.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, String, text
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class Conversation(SQLModel, table=True):
    """Conversation entity for AI chat sessions.

    One user can have multiple conversations (different topics/contexts).
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

    user_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    openai_thread_id: str = Field(
        default="",
        sa_column=Column(String(255), nullable=True, default=""),
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    last_message_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
