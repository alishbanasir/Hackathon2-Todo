"""UpdateTodoTool for modifying todo details via AI assistant.

Handles natural language todo updates with ownership verification.
"""

from typing import Any, Dict, Optional
from uuid import UUID

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.base import MCPTool

logger = structlog.get_logger(__name__)


class UpdateTodoTool(MCPTool):
    """MCP tool for updating todo details.

    Accepts todo_id (required) and optional title, description, completed parameters.
    Only allows users to update their own todos (FR-012).
    At least one field must be provided for update.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize UpdateTodoTool.

        Args:
            session: Database session for todo updates
        """
        super().__init__(
            name="update_todo",
            description="Update a todo's title, description, or completion status",
        )
        self.session = session

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate todo update parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If validation fails
        """
        # todo_id is required
        if "todo_id" not in parameters:
            raise ValueError("todo_id is required")

        todo_id = parameters["todo_id"]

        # todo_id must be an integer
        if not isinstance(todo_id, int):
            raise ValueError("todo_id must be an integer")

        # todo_id must be positive
        if todo_id <= 0:
            raise ValueError("todo_id must be a positive integer")

        # At least one field must be provided for update
        has_update = False
        if "title" in parameters:
            has_update = True
            title = parameters["title"]

            # Title must be string if provided
            if not isinstance(title, str):
                raise ValueError("title must be a string")

            # Title length validation (1-200 characters)
            if len(title) < 1:
                raise ValueError("title must be at least 1 character")
            if len(title) > 200:
                raise ValueError("title must not exceed 200 characters")

        if "description" in parameters:
            has_update = True
            description = parameters["description"]

            # Description must be string if provided
            if not isinstance(description, str):
                raise ValueError("description must be a string")

            # Description length validation (0-2000 characters)
            if len(description) > 2000:
                raise ValueError("description must not exceed 2000 characters")

        if "completed" in parameters:
            has_update = True
            completed = parameters["completed"]

            # Completed must be boolean if provided
            if not isinstance(completed, bool):
                raise ValueError("completed must be a boolean")

        # Ensure at least one field is being updated
        if not has_update:
            raise ValueError(
                "At least one field (title, description, or completed) must be provided for update"
            )

    async def execute(
        self,
        parameters: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Update a todo with ownership verification (FR-009, FR-012).

        Args:
            parameters: Tool parameters (todo_id, optional: title, description, completed)
            user_id: Authenticated user ID from JWT token (FR-011, FR-031)

        Returns:
            Success result with updated todo or error

        Example Success:
            ```json
            {
                "success": true,
                "todo_id": 42,
                "title": "Updated title",
                "description": "Updated description",
                "completed": false,
                "message": "Todo updated successfully"
            }
            ```

        Example Error (Not Found):
            ```json
            {
                "success": false,
                "error": "not_found",
                "message": "Todo not found or you don't have permission to update it"
            }
            ```

        Example Error (Validation):
            ```json
            {
                "success": false,
                "error": "validation_error",
                "message": "title must be at least 1 character"
            }
            ```
        """
        try:
            # Validate parameters
            self.validate_parameters(parameters)

            todo_id = parameters["todo_id"]

            # Build dynamic UPDATE query based on provided fields
            update_fields = []
            update_params: Dict[str, Any] = {
                "todo_id": todo_id,
                "user_id": user_id,
            }

            if "title" in parameters:
                update_fields.append("title = :title")
                update_params["title"] = parameters["title"]

            if "description" in parameters:
                update_fields.append("description = :description")
                update_params["description"] = parameters["description"]

            if "completed" in parameters:
                update_fields.append("completed = :completed")
                update_params["completed"] = parameters["completed"]

            # Build and execute UPDATE query with ownership verification (FR-012)
            query = text(f"""
                UPDATE todos
                SET {', '.join(update_fields)}
                WHERE id = :todo_id AND user_id = :user_id
                RETURNING id, title, description, completed, created_at
            """)

            result = await self.session.execute(query, update_params)
            updated_todo = result.fetchone()

            # Commit the transaction
            await self.session.commit()

            # Check if todo was found and updated
            if not updated_todo:
                # Todo doesn't exist or doesn't belong to user (FR-012)
                logger.warning(
                    "todo_update_not_found",
                    user_id=str(user_id),
                    todo_id=todo_id,
                )
                return {
                    "success": False,
                    "error": "not_found",
                    "message": "Todo not found or you don't have permission to update it",
                }

            logger.info(
                "todo_updated",
                user_id=str(user_id),
                todo_id=todo_id,
                updated_fields=list(parameters.keys()),
            )

            return {
                "success": True,
                "todo_id": updated_todo.id,
                "title": updated_todo.title,
                "description": updated_todo.description,
                "completed": updated_todo.completed,
                "message": "Todo updated successfully",
            }

        except ValueError as e:
            # Validation error
            logger.warning(
                "todo_update_validation_error",
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
                "todo_update_failed",
                user_id=str(user_id),
                error=str(e),
                parameters=parameters,
                exc_info=True,
            )
            return {
                "success": False,
                "error": "database_error",
                "message": "Failed to update todo. Please try again.",
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
                        "todo_id": {
                            "type": "integer",
                            "description": "ID of the todo to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "New title (1-200 characters)",
                        },
                        "description": {
                            "type": "string",
                            "description": "New description (0-2000 characters)",
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "New completion status",
                        },
                    },
                    "required": ["todo_id"],
                },
            },
        }
