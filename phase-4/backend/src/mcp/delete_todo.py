"""DeleteTodoTool for removing todos via AI assistant.

Handles natural language todo deletion with ownership verification.
"""

from typing import Any, Dict
from uuid import UUID

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.base import MCPTool

logger = structlog.get_logger(__name__)


class DeleteTodoTool(MCPTool):
    """MCP tool for deleting todos permanently.

    Accepts todo_id parameter and enforces ownership verification.
    Only allows users to delete their own todos (FR-012).
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize DeleteTodoTool.

        Args:
            session: Database session for todo deletion
        """
        super().__init__(
            name="delete_todo",
            description="Delete a todo permanently",
        )
        self.session = session

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate todo deletion parameters.

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

    async def execute(
        self,
        parameters: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Delete a todo with ownership verification (FR-010, FR-012).

        Args:
            parameters: Tool parameters (todo_id)
            user_id: Authenticated user ID from JWT token (FR-011, FR-031)

        Returns:
            Success result with deletion confirmation or error

        Example Success:
            ```json
            {
                "success": true,
                "todo_id": 42,
                "title": "Old task",
                "message": "Todo deleted successfully"
            }
            ```

        Example Error (Not Found):
            ```json
            {
                "success": false,
                "error": "not_found",
                "message": "Todo not found or you don't have permission to delete it"
            }
            ```

        Example Error (Authorization):
            ```json
            {
                "success": false,
                "error": "authorization_error",
                "message": "You don't have permission to delete this todo"
            }
            ```
        """
        try:
            # Validate parameters
            self.validate_parameters(parameters)

            todo_id = parameters["todo_id"]

            # First, get todo details for logging (before deletion)
            select_query = text("""
                SELECT id, title, user_id
                FROM todos
                WHERE id = :todo_id
            """)

            select_result = await self.session.execute(
                select_query,
                {"todo_id": todo_id},
            )
            todo_before_delete = select_result.fetchone()

            # Check if todo exists
            if not todo_before_delete:
                logger.warning(
                    "todo_delete_not_found",
                    user_id=str(user_id),
                    todo_id=todo_id,
                )
                return {
                    "success": False,
                    "error": "not_found",
                    "message": "Todo not found or you don't have permission to delete it",
                }

            # Check ownership (FR-012)
            if todo_before_delete.user_id != user_id:
                logger.warning(
                    "todo_delete_unauthorized",
                    user_id=str(user_id),
                    todo_id=todo_id,
                    owner_id=str(todo_before_delete.user_id),
                )
                return {
                    "success": False,
                    "error": "authorization_error",
                    "message": "You don't have permission to delete this todo",
                }

            # Delete todo with ownership verification (FR-012)
            delete_query = text("""
                DELETE FROM todos
                WHERE id = :todo_id AND user_id = :user_id
                RETURNING id, title
            """)

            delete_result = await self.session.execute(
                delete_query,
                {"todo_id": todo_id, "user_id": user_id},
            )
            deleted_todo = delete_result.fetchone()

            # Commit the transaction
            await self.session.commit()

            # Double-check deletion succeeded
            if not deleted_todo:
                # Should not happen given checks above, but handle defensively
                logger.error(
                    "todo_delete_unexpected_failure",
                    user_id=str(user_id),
                    todo_id=todo_id,
                )
                return {
                    "success": False,
                    "error": "database_error",
                    "message": "Failed to delete todo. Please try again.",
                }

            logger.info(
                "todo_deleted",
                user_id=str(user_id),
                todo_id=todo_id,
                title=deleted_todo.title,
            )

            return {
                "success": True,
                "todo_id": deleted_todo.id,
                "title": deleted_todo.title,
                "message": "Todo deleted successfully",
            }

        except ValueError as e:
            # Validation error
            logger.warning(
                "todo_delete_validation_error",
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
                "todo_delete_failed",
                user_id=str(user_id),
                error=str(e),
                parameters=parameters,
                exc_info=True,
            )
            return {
                "success": False,
                "error": "database_error",
                "message": "Failed to delete todo. Please try again.",
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
                            "description": "ID of the todo to delete permanently",
                        },
                    },
                    "required": ["todo_id"],
                },
            },
        }
