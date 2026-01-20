"""MCP (Model Context Protocol) tools for AI assistant interactions.

Provides tools that the OpenAI Assistant can invoke to perform todo operations.
"""

from src.mcp.add_todo import AddTodoTool
from src.mcp.base import MCPTool
from src.mcp.complete_todo import CompleteTodoTool
from src.mcp.delete_todo import DeleteTodoTool
from src.mcp.list_todos import ListTodosTool
from src.mcp.update_todo import UpdateTodoTool
from src.mcp.tool_registry import ToolRegistry

__all__ = [
    "MCPTool",
    "AddTodoTool",
    "ListTodosTool",
    "CompleteTodoTool",
    "DeleteTodoTool",
    "UpdateTodoTool",
    "ToolRegistry",
]
