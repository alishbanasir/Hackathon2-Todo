"""Todo request/response schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TodoCreateRequest(BaseModel):
    """Request schema for creating a new todo.

    Attributes:
        title: Todo title (1-200 characters, required)
        description: Todo description (0-2000 characters, optional)
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Todo title",
        examples=["Complete project documentation"]
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Todo description (optional)",
        examples=["Write comprehensive API docs"]
    )


class TodoUpdateRequest(BaseModel):
    """Request schema for updating a todo.

    Attributes:
        title: New title (1-200 characters, optional)
        description: New description (0-2000 characters, optional)
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="New title (optional)",
        examples=["Updated project documentation"]
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="New description (optional)",
        examples=["Updated comprehensive API docs"]
    )


class TodoResponse(BaseModel):
    """Response schema for todo data.

    Attributes:
        id: Todo's unique identifier
        user_id: Owner's user ID
        title: Todo title
        description: Todo description
        completed: Completion status
        created_at: Creation timestamp (UTC)
    """

    id: int = Field(..., description="Todo's unique identifier")
    user_id: UUID = Field(..., description="Owner's user ID")
    title: str = Field(..., description="Todo title")
    description: str = Field(..., description="Todo description")
    completed: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Allow creation from SQLModel
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Complete project documentation",
                "description": "Write comprehensive API docs",
                "completed": False,
                "created_at": "2026-01-07T12:00:00Z"
            }
        }


class TodoListResponse(BaseModel):
    """Response schema for list of todos.

    Attributes:
        todos: List of todos
        total: Total count of todos
    """

    todos: list[TodoResponse] = Field(..., description="List of todos")
    total: int = Field(..., description="Total count of todos")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "todos": [
                    {
                        "id": 1,
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Complete project documentation",
                        "description": "Write comprehensive API docs",
                        "completed": False,
                        "created_at": "2026-01-07T12:00:00Z"
                    }
                ],
                "total": 1
            }
        }
