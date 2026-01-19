"""Phase 3 database models.

Exports all models for centralized import and Alembic metadata discovery.
Uses pure SQLAlchemy ORM (no SQLModel) for Pydantic v2 compatibility.
"""

# Import Base and User first - needed for foreign key references
from src.models.user import Base, User

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole

__all__ = ["Base", "User", "Conversation", "Message", "MessageRole"]
