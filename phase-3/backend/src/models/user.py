"""User model reference for Phase 3.

This is a minimal model that mirrors the Phase 2 User table structure.
It allows SQLAlchemy to recognize the 'users' table for foreign key references
without duplicating business logic. The actual User table is managed by Phase 2.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, String


class User(SQLModel, table=True):
    """User entity - mirrors Phase 2 users table for FK references."""

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
