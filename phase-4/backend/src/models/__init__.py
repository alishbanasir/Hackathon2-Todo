"""Domain models for the Todo application."""

from sqlmodel import SQLModel

from src.models.todo import Todo
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole

# Expose SQLModel.metadata as Base for table auto-creation
Base = SQLModel.metadata

__all__ = ["SQLModel", "User", "Todo", "Conversation", "Message", "MessageRole", "Base"]
