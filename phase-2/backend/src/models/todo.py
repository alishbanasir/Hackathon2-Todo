"""Todo domain model."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import Column, Field, ForeignKey, SQLModel, String


class Todo(SQLModel, table=True):
    """Todo entity representing a single task item owned by a user.

    Attributes:
        id: Unique todo identifier (auto-incrementing integer)
        user_id: Foreign key to User.id (owner of this todo)
        title: Todo title (1-200 characters, required)
        description: Todo description (0-2000 characters, optional)
        completed: Completion status (default: False)
        created_at: Todo creation timestamp (UTC)
    """

    __tablename__ = "todos"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
    )

    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    title: str = Field(
        sa_column=Column(String(200), nullable=False)
    )

    description: str = Field(
        default="",
        sa_column=Column(String(2000), nullable=False, server_default=""),
    )

    completed: bool = Field(
        default=False,
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the API",
                "completed": False,
                "created_at": "2026-01-07T12:00:00Z",
            }
        }
