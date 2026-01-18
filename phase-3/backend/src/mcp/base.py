"""Base class for MCP tools.

Defines the abstract interface that all MCP tools must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID

import structlog

logger = structlog.get_logger(__name__)


class MCPTool(ABC):
    """Abstract base class for MCP (Model Context Protocol) tools.

    All MCP tools must inherit from this class and implement the execute() method.
    Tools are invoked by the OpenAI Assistant via function calling.
    """

    def __init__(self, name: str, description: str) -> None:
        """Initialize MCP tool.

        Args:
            name: Tool name (must match OpenAI function name)
            description: Human-readable description of what the tool does
        """
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(
        self,
        parameters: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Execute the tool with given parameters.

        Args:
            parameters: Tool parameters from OpenAI function call
            user_id: Authenticated user ID from JWT token (for user isolation)

        Returns:
            Tool execution result as dictionary

        Raises:
            ValueError: If parameters are invalid
            Exception: If tool execution fails

        Example:
            ```python
            class AddTodoTool(MCPTool):
                async def execute(self, parameters: Dict[str, Any], user_id: UUID):
                    title = parameters["title"]
                    description = parameters.get("description", "")
                    # Create todo in database...
                    return {"success": True, "todo_id": 42, "title": title}
            ```
        """
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate tool parameters before execution.

        Args:
            parameters: Parameters to validate

        Raises:
            ValueError: If parameters are invalid
        """
        # Default implementation - subclasses can override
        pass

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function definition.

        Returns:
            OpenAI function definition dictionary

        Note:
            Subclasses should override this to provide specific parameter schemas.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }
