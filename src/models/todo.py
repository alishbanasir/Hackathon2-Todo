"""Todo domain model - Pure SQLAlchemy ORM."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID

from src.models.user import Base


class Todo(Base):
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

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        String(2000),
        nullable=False,
        server_default="",
    )

    completed = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
