"""Todo service for business logic."""

from typing import List, Optional
from uuid import UUID

from src.models.todo import Todo
from src.repositories.todo_repository import TodoRepository


class TodoService:
    """Service for todo business logic."""

    def __init__(self, repository: TodoRepository):
        """Initialize TodoService.

        Args:
            repository: Repository for todo data access
        """
        self.repository = repository

    async def create_todo(
        self, title: str, description: str, user_id: UUID
    ) -> Todo:
        """Create a new todo with validation.

        Args:
            title: Todo title (1-200 characters)
            description: Todo description (0-2000 characters)
            user_id: Owner's user ID

        Returns:
            Created todo

        Raises:
            ValueError: If validation fails
        """
        # Validate title
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title must be 200 characters or less")

        # Validate description
        if len(description) > 2000:
            raise ValueError("Description must be 2000 characters or less")

        return await self.repository.create_todo(title, description, user_id)

    async def get_user_todos(self, user_id: UUID) -> List[Todo]:
        """Get all todos for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of user's todos
        """
        return await self.repository.get_user_todos(user_id)

    async def get_todo_by_id(self, todo_id: int, user_id: UUID) -> Optional[Todo]:
        """Get a specific todo with ownership verification.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier

        Returns:
            Todo if found and owned by user, None otherwise
        """
        return await self.repository.get_by_id(todo_id, user_id)

    async def update_todo(
        self,
        todo_id: int,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Todo]:
        """Update a todo with validation.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier
            title: New title (optional)
            description: New description (optional)

        Returns:
            Updated todo if found and owned by user, None otherwise

        Raises:
            ValueError: If validation fails
        """
        # Validate title if provided
        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("Title cannot be empty")
            if len(title) > 200:
                raise ValueError("Title must be 200 characters or less")

        # Validate description if provided
        if description is not None and len(description) > 2000:
            raise ValueError("Description must be 2000 characters or less")

        return await self.repository.update_todo(
            todo_id, user_id, title, description
        )

    async def toggle_completion(
        self, todo_id: int, user_id: UUID
    ) -> Optional[Todo]:
        """Toggle a todo's completion status.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier

        Returns:
            Updated todo if found and owned by user, None otherwise
        """
        return await self.repository.toggle_completion(todo_id, user_id)

    async def delete_todo(self, todo_id: int, user_id: UUID) -> bool:
        """Delete a todo.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier

        Returns:
            True if deleted, False if not found or not owned by user
        """
        return await self.repository.delete_todo(todo_id, user_id)
