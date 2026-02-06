"""Message model for chat history persistence.

Stores all messages (user and assistant) for audit trail and conversation history.
Messages belong to conversations and are displayed in chronological order.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, Text
from sqlalchemy import ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class MessageRole(str, Enum):
    """Message role enumeration."""

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
    )

    conversation_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    role: str = Field(
        sa_column=Column(
            SQLEnum(MessageRole, name="message_role", native_enum=False),
            nullable=False,
        )
    )

    content: str = Field(
        sa_column=Column(Text, nullable=False),
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
