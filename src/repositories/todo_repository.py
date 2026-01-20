"""Todo repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.models.todo import Todo


class TodoRepository:
    """Repository for Todo entity data access."""

    async def create_todo(
        self, title: str, description: str, user_id: UUID
    ) -> Todo:
        """Create a new todo in the database.

        Args:
            title: Todo title (1-200 characters)
            description: Todo description (0-2000 characters)
            user_id: Owner's user ID

        Returns:
            Created todo with generated ID and timestamp
        """
        async with async_session_maker() as session:
            todo = Todo(title=title, description=description, user_id=user_id)
            session.add(todo)
            await session.commit()
            await session.refresh(todo)
            return todo

    async def get_user_todos(self, user_id: UUID) -> List[Todo]:
        """Retrieve all todos belonging to a user, ordered by creation date (newest first).

        Args:
            user_id: User's unique identifier

        Returns:
            List of todos owned by the user
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(Todo)
                .where(Todo.user_id == user_id)
                .order_by(Todo.created_at.desc())
            )
            return list(result.scalars().all())

    async def get_by_id(self, todo_id: int, user_id: UUID) -> Optional[Todo]:
        """Retrieve a specific todo by ID, ensuring ownership.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier (for ownership verification)

        Returns:
            Todo if found and owned by user, None otherwise
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
            )
            return result.scalars().first()

    async def update_todo(
        self,
        todo_id: int,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Todo]:
        """Update a todo's title and/or description.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier (for ownership verification)
            title: New title (if provided)
            description: New description (if provided)

        Returns:
            Updated todo if found and owned by user, None otherwise
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
            )
            todo = result.scalars().first()

            if not todo:
                return None

            if title is not None:
                todo.title = title
            if description is not None:
                todo.description = description

            session.add(todo)
            await session.commit()
            await session.refresh(todo)
            return todo

    async def toggle_completion(
        self, todo_id: int, user_id: UUID
    ) -> Optional[Todo]:
        """Toggle a todo's completion status.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier (for ownership verification)

        Returns:
            Updated todo if found and owned by user, None otherwise
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
            )
            todo = result.scalars().first()

            if not todo:
                return None

            todo.completed = not todo.completed

            session.add(todo)
            await session.commit()
            await session.refresh(todo)
            return todo

    async def delete_todo(self, todo_id: int, user_id: UUID) -> bool:
        """Delete a todo.

        Args:
            todo_id: Todo's unique identifier
            user_id: User's unique identifier (for ownership verification)

        Returns:
            True if deleted, False if not found or not owned by user
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
            )
            todo = result.scalars().first()

            if not todo:
                return False

            await session.delete(todo)
            await session.commit()
            return True
