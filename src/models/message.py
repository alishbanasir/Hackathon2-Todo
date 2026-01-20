"""Message model for chat history persistence.

Stores all messages (user and assistant) for audit trail and conversation history.
Messages belong to conversations and are displayed in chronological order.
"""

from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Text, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from src.models.user import Base


class MessageRole(str, Enum):
    """Message role enumeration.

    Distinguishes between user-sent messages and AI assistant responses.
    """

    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    """Message entity for chat history.

    Persists all messages in conversations for audit trail and history retrieval.
    Each message belongs to exactly one conversation and has a role (user or assistant).
    """

    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(
        SQLEnum(MessageRole, name="message_role", native_enum=False),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=text("CURRENT_TIMESTAMP"),
    )
