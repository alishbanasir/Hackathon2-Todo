"""CompleteTodoTool for marking todos as completed via AI assistant.

Handles natural language todo completion with ownership verification.
"""

from typing import Any, Dict
from uuid import UUID

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.base import MCPTool

logger = structlog.get_logger(__name__)


class CompleteTodoTool(MCPTool):
    """MCP tool for marking todos as completed.

    Accepts todo_id parameter and enforces ownership verification.
    Only allows users to complete their own todos (FR-012).
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize CompleteTodoTool.

        Args:
            session: Database session for todo updates
        """
        super().__init__(
            name="complete_todo",
            description="Mark a todo as completed",
        )
        self.session = session

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate todo completion parameters.

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
        """Mark a todo as completed with ownership verification (FR-008, FR-012).

        Args:
            parameters: Tool parameters (todo_id)
            user_id: Authenticated user ID from JWT token (FR-011, FR-031)

        Returns:
            Success result with completed todo or error

        Example Success:
            ```json
            {
                "success": true,
                "todo_id": 42,
                "title": "Buy groceries",
                "completed": true,
                "message": "Todo marked as completed"
            }
            ```

        Example Error (Not Found):
            ```json
            {
                "success": false,
                "error": "not_found",
                "message": "Todo not found or you don't have permission to complete it"
            }
            ```

        Example Error (Validation):
            ```json
            {
                "success": false,
                "error": "validation_error",
                "message": "todo_id must be a positive integer"
            }
            ```
        """
        try:
            # Validate parameters
            self.validate_parameters(parameters)

            todo_id = parameters["todo_id"]

            # Update todo with ownership verification (FR-012)
            # This ensures user can only complete their own todos
            query = text("""
                UPDATE todos
                SET completed = true
                WHERE id = :todo_id AND user_id = :user_id
                RETURNING id, title, description, completed
            """)

            result = await self.session.execute(
                query,
                {"todo_id": todo_id, "user_id": user_id},
            )
            todo_row = result.fetchone()

            # Commit the transaction
            await self.session.commit()

            # Check if todo was found and updated
            if not todo_row:
                # Todo doesn't exist or doesn't belong to user (FR-012)
                logger.warning(
                    "todo_complete_not_found",
                    user_id=str(user_id),
                    todo_id=todo_id,
                )
                return {
                    "success": False,
                    "error": "not_found",
                    "message": "Todo not found or you don't have permission to complete it",
                }

            logger.info(
                "todo_completed",
                user_id=str(user_id),
                todo_id=todo_id,
                title=todo_row.title,
            )

            return {
                "success": True,
                "todo_id": todo_row.id,
                "title": todo_row.title,
                "completed": todo_row.completed,
                "message": "Todo marked as completed",
            }

        except ValueError as e:
            # Validation error
            logger.warning(
                "todo_complete_validation_error",
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
                "todo_complete_failed",
                user_id=str(user_id),
                error=str(e),
                parameters=parameters,
                exc_info=True,
            )
            return {
                "success": False,
                "error": "database_error",
                "message": "Failed to complete todo. Please try again.",
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
                            "description": "ID of the todo to mark as complete",
                        },
                    },
                    "required": ["todo_id"],
                },
            },
        }
