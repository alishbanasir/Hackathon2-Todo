"""Conversation model for tracking chat sessions.

Each conversation represents a unique chat session between a user and the AI assistant,
mapped to a Gemini context for context preservation.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID

from src.models.user import Base


class Conversation(Base):
    """Conversation entity for AI chat sessions.

    Maps to Gemini API contexts for context management.
    One user can have multiple conversations (different topics/contexts).
    """

    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    openai_thread_id = Column(
        String(255),
        nullable=True,
        unique=False,
        default="",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    last_message_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=text("CURRENT_TIMESTAMP"),
    )
