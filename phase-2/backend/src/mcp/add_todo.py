"""AddTodoTool for creating new todos via AI assistant.

Handles natural language todo creation with title and optional description.
"""

from typing import Any, Dict
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.mcp.base import MCPTool

logger = structlog.get_logger(__name__)


class AddTodoTool(MCPTool):
    """MCP tool for adding new todos.

    Accepts title (required, 1-200 chars) and description (optional, 0-2000 chars).
    Enforces user isolation by injecting user_id from execution context.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize AddTodoTool.

        Args:
            session: Database session for todo creation
        """
        super().__init__(
            name="add_todo",
            description="Create a new todo item for the user",
        )
        self.session = session

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate todo parameters (FR-037).

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If validation fails
        """
        # Title is required
        if "title" not in parameters:
            raise ValueError("Title is required")

        title = parameters["title"]

        # Title must be a string
        if not isinstance(title, str):
            raise ValueError("Title must be a string")

        # Title must not be empty after stripping whitespace
        if not title.strip():
            raise ValueError("Title cannot be empty")

        # Title length: 1-200 characters (FR-037)
        if len(title) > 200:
            raise ValueError("Title must be 200 characters or less")

        # Description is optional
        if "description" in parameters:
            description = parameters["description"]

            # Description must be a string if provided
            if not isinstance(description, str):
                raise ValueError("Description must be a string")

            # Description length: 0-2000 characters (FR-037)
            if len(description) > 2000:
                raise ValueError("Description must be 2000 characters or less")

    async def execute(
        self,
        parameters: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Create a new todo item (FR-006, FR-011).

        Args:
            parameters: Tool parameters (title, optional description)
            user_id: Authenticated user ID from JWT token (FR-011, FR-031)

        Returns:
            Success result with todo details or error

        Example Success:
            ```json
            {
                "success": true,
                "todo_id": 42,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": false
            }
            ```

        Example Error:
            ```json
            {
                "success": false,
                "error": "validation_error",
                "message": "Title must be 200 characters or less"
            }
            ```
        """
        try:
            # Validate parameters (FR-037)
            self.validate_parameters(parameters)

            title = parameters["title"].strip()
            description = parameters.get("description", "").strip()

            # Create todo using raw SQL insert (Phase 2 todos table)
            # Note: Phase 3 shares the same database with Phase 2
            # The todos table exists from Phase 2 migration
            from datetime import datetime, timezone
            from sqlalchemy import text

            # Insert todo with user_id from JWT (FR-011, FR-031)
            # NOT from parameters - user isolation enforcement
            insert_query = text("""
                INSERT INTO todos (user_id, title, description, completed, created_at)
                VALUES (:user_id, :title, :description, :completed, :created_at)
                RETURNING id, user_id, title, description, completed, created_at
            """)

            result = await self.session.execute(
                insert_query,
                {
                    "user_id": user_id,
                    "title": title,
                    "description": description,
                    "completed": False,
                    "created_at": datetime.now(timezone.utc),
                },
            )
            todo_row = result.fetchone()

            # Commit the transaction
            await self.session.commit()

            logger.info(
                "todo_created",
                user_id=str(user_id),
                todo_id=todo_row.id,
                title=title,
            )

            return {
                "success": True,
                "todo_id": todo_row.id,
                "title": todo_row.title,
                "description": todo_row.description,
                "completed": todo_row.completed,
            }

        except ValueError as e:
            # Validation error (FR-037)
            logger.warning(
                "todo_validation_error",
                user_id=str(user_id),
                error=str(e),
                parameters=parameters,
            )
            return {
                "success": False,
                "error": "validation_error",
                "message": str(e),
            }

        except Exception as e:
            # Database or unexpected error (FR-035)
            logger.error(
                "todo_creation_failed",
                user_id=str(user_id),
                error=str(e),
                parameters=parameters,
                exc_info=True,
            )
            return {
                "success": False,
                "error": "database_error",
                "message": "Failed to create todo. Please try again.",
            }

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function definition.

        Returns:
            OpenAI function definition with JSON Schema parameters
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Todo title (1-200 characters, required)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description (0-2000 characters)",
                        },
                    },
                    "required": ["title"],
                },
            },
        }
