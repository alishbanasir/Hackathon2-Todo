"""ListTodosTool for retrieving user's todos via AI assistant.

Handles natural language todo listing with optional completion status filter.
"""

from typing import Any, Dict, Optional
from uuid import UUID

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.base import MCPTool

logger = structlog.get_logger(__name__)


class ListTodosTool(MCPTool):
    """MCP tool for listing user's todos.

    Accepts optional completed filter (boolean or null for all todos).
    Enforces user isolation by filtering by user_id from execution context.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ListTodosTool.

        Args:
            session: Database session for todo retrieval
        """
        super().__init__(
            name="list_todos",
            description="List user's todos, optionally filtered by completion status",
        )
        self.session = session

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate todo listing parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If validation fails
        """
        # Completed filter is optional
        if "completed" in parameters:
            completed = parameters["completed"]

            # Must be boolean if provided
            if not isinstance(completed, bool) and completed is not None:
                raise ValueError("Completed filter must be true, false, or omitted")

    async def execute(
        self,
        parameters: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """List user's todos with optional filtering (FR-007, FR-013).

        Args:
            parameters: Tool parameters (optional completed filter)
            user_id: Authenticated user ID from JWT token (FR-011, FR-031)

        Returns:
            Success result with todo list or error

        Example Success:
            ```json
            {
                "success": true,
                "todos": [
                    {
                        "id": 1,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": false,
                        "created_at": "2026-01-13T10:00:00Z"
                    },
                    {
                        "id": 2,
                        "title": "Project report",
                        "description": "",
                        "completed": true,
                        "created_at": "2026-01-12T15:30:00Z"
                    }
                ],
                "total_count": 2,
                "filter": "all"
            }
            ```

        Example Error:
            ```json
            {
                "success": false,
                "error": "database_error",
                "message": "Failed to retrieve todos. Please try again."
            }
            ```
        """
        try:
            # Validate parameters
            self.validate_parameters(parameters)

            # Extract completed filter (optional)
            completed_filter: Optional[bool] = parameters.get("completed")

            # Build query with user isolation (FR-011)
            if completed_filter is None:
                # Get all todos for user
                query = text("""
                    SELECT id, user_id, title, description, completed, created_at
                    FROM todos
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                """)
                params = {"user_id": user_id}
                filter_description = "all"
            else:
                # Filter by completion status
                query = text("""
                    SELECT id, user_id, title, description, completed, created_at
                    FROM todos
                    WHERE user_id = :user_id AND completed = :completed
                    ORDER BY created_at DESC
                """)
                params = {"user_id": user_id, "completed": completed_filter}
                filter_description = "completed" if completed_filter else "pending"

            # Execute query
            result = await self.session.execute(query, params)
            rows = result.fetchall()

            # Convert rows to dictionaries
            todos = []
            for row in rows:
                todos.append({
                    "id": row.id,
                    "title": row.title,
                    "description": row.description,
                    "completed": row.completed,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })

            logger.info(
                "todos_listed",
                user_id=str(user_id),
                todo_count=len(todos),
                filter=filter_description,
            )

            return {
                "success": True,
                "todos": todos,
                "total_count": len(todos),
                "filter": filter_description,
            }

        except ValueError as e:
            # Validation error
            logger.warning(
                "todo_list_validation_error",
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
                "todo_list_failed",
                user_id=str(user_id),
                error=str(e),
                parameters=parameters,
                exc_info=True,
            )
            return {
                "success": False,
                "error": "database_error",
                "message": "Failed to retrieve todos. Please try again.",
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
                        "completed": {
                            "type": "boolean",
                            "description": "Optional filter: true for completed todos, false for pending, omit for all",
                        },
                    },
                    "required": [],
                },
            },
        }
