"""User model reference for Phase 3.

This is a minimal model that mirrors the Phase 2 User table structure.
It allows SQLAlchemy to recognize the 'users' table for foreign key references
without duplicating business logic. The actual User table is managed by Phase 2.
"""

from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User entity - mirrors Phase 2 users table for FK references."""

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
