"""Tool registry for mapping MCP tools to OpenAI function definitions.

Maintains a registry of all available MCP tools and provides methods
to convert them to OpenAI Assistants API function definitions.
"""

from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.add_todo import AddTodoTool
from src.mcp.base import MCPTool
from src.mcp.complete_todo import CompleteTodoTool
from src.mcp.delete_todo import DeleteTodoTool
from src.mcp.list_todos import ListTodosTool
from src.mcp.update_todo import UpdateTodoTool

logger = structlog.get_logger(__name__)


class ToolRegistry:
    """Registry for MCP tools available to the AI assistant.

    Manages tool instantiation and provides OpenAI function definitions.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize tool registry.

        Args:
            session: Database session for tools that need database access
        """
        self.session = session
        self._tools: Dict[str, MCPTool] = {}
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all available MCP tools.

        Currently registers:
        - add_todo: Create new todo items (US1)
        - list_todos: List user's todos with optional filtering (US2)
        - complete_todo: Mark todo as completed (US2)
        - delete_todo: Delete todo permanently (US2)
        - update_todo: Update todo title, description, or status (US3)
        """
        # US1: Natural Language Todo Creation
        add_todo_tool = AddTodoTool(session=self.session)
        self._tools[add_todo_tool.name] = add_todo_tool

        # US2: Conversational Todo Management
        list_todos_tool = ListTodosTool(session=self.session)
        self._tools[list_todos_tool.name] = list_todos_tool

        complete_todo_tool = CompleteTodoTool(session=self.session)
        self._tools[complete_todo_tool.name] = complete_todo_tool

        delete_todo_tool = DeleteTodoTool(session=self.session)
        self._tools[delete_todo_tool.name] = delete_todo_tool

        # US3: Todo Updates and Modifications
        update_todo_tool = UpdateTodoTool(session=self.session)
        self._tools[update_todo_tool.name] = update_todo_tool

        logger.info(
            "tools_registered",
            tool_count=len(self._tools),
            tool_names=list(self._tools.keys()),
        )

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get tool by name.

        Args:
            name: Tool name

        Returns:
            MCPTool instance if found, None otherwise
        """
        return self._tools.get(name)

    def get_all_tools(self) -> List[MCPTool]:
        """Get all registered tools.

        Returns:
            List of all MCPTool instances
        """
        return list(self._tools.values())

    def to_openai_functions(self) -> List[Dict[str, Any]]:
        """Convert all tools to OpenAI function definitions.

        Returns:
            List of OpenAI function definition dictionaries

        Example:
            ```json
            [
                {
                    "type": "function",
                    "function": {
                        "name": "add_todo",
                        "description": "Create a new todo item for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Todo title (1-200 characters)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Optional description"
                                }
                            },
                            "required": ["title"]
                        }
                    }
                }
            ]
            ```
        """
        return [tool.to_openai_function() for tool in self._tools.values()]

    def has_tool(self, name: str) -> bool:
        """Check if tool is registered.

        Args:
            name: Tool name

        Returns:
            True if tool exists, False otherwise
        """
        return name in self._tools

    def tool_count(self) -> int:
        """Get total number of registered tools.

        Returns:
            Number of tools in registry
        """
        return len(self._tools)
