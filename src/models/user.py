"""User domain model."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, String


class User(SQLModel, table=True):
    """User entity representing an authenticated application user.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique, indexed)
        password_hash: Argon2id hashed password (never store plaintext)
        created_at: Account creation timestamp (UTC)
    """

    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False)
    )

    password_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2026-01-07T12:00:00Z",
            }
        }
