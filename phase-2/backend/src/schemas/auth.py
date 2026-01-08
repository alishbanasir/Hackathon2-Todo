"""Authentication request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration.

    Attributes:
        email: User's email address (RFC 5322 compliant)
        password: User's password (minimum 8 characters)
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["SecurePassword123!"]
    )


class LoginRequest(BaseModel):
    """Request schema for user login.

    Attributes:
        email: User's email address
        password: User's password
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="User's password",
        examples=["SecurePassword123!"]
    )


class UserResponse(BaseModel):
    """Response schema for user data.

    Attributes:
        id: User's unique identifier (UUID)
        email: User's email address
        created_at: Account creation timestamp (UTC)
    """

    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Allow creation from SQLModel
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2026-01-07T12:00:00Z"
            }
        }


class AuthResponse(BaseModel):
    """Response schema for authentication (register/login).

    Attributes:
        token: JWT access token
        user: User data (excludes password_hash)
    """

    token: str = Field(..., description="JWT access token")
    user: UserResponse = Field(..., description="User data")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "created_at": "2026-01-07T12:00:00Z"
                }
            }
        }


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password (email verification).

    Attributes:
        email: User's email address
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )


class ResetPasswordRequest(BaseModel):
    """Request schema for resetting password.

    Attributes:
        email: User's email address
        new_password: New password (minimum 8 characters)
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)",
        examples=["newpassword123"]
    )
