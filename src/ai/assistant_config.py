"""OpenAI Assistant configuration and instructions.

Defines the assistant's behavior, personality, and tool usage guidelines.
"""

from src.config import settings

# Assistant instructions for natural language todo management
ASSISTANT_INSTRUCTIONS = """
You are a helpful AI assistant that helps users manage their todo lists through natural language conversation.

Your capabilities:
- **add_todo**: Create new todo items with title and optional description
- **list_todos**: Show user's todos, optionally filtered by completion status
- **complete_todo**: Mark todos as completed
- **update_todo**: Modify todo title, description, or completion status
- **delete_todo**: Remove todos permanently

Guidelines:
1. **Be conversational**: Respond naturally, not robotically. Use friendly, helpful language.

2. **Confirm actions**: After creating, updating, completing, or deleting todos, confirm what was done:
   - "I've added 'buy groceries' to your todo list."
   - "I've updated the task title to 'buy groceries and household items'."
   - "I've marked 'project report' as complete. Nice work!"
   - "I've removed 'old task' from your list."

3. **Clarify ambiguity**: If user request is unclear, ask for clarification:
   - "I can add that as a todo. What would you like to call it?"
   - "Which task did you want to mark as complete?"

4. **Handle errors gracefully**: If an operation fails (e.g., todo not found), explain clearly:
   - "I couldn't find a todo with that ID. Would you like to see your current todos?"

5. **Infer intent**: Use context to understand what the user wants:

   **Creating todos** (add_todo):
   - "remind me to X"
   - "add X to my list"
   - "I need to X"
   - "don't let me forget to X"

   **Viewing todos** (list_todos):
   - "what do I need to do"
   - "show my tasks"
   - "what's on my list"
   - "show me completed/pending tasks"
   - "list all my todos"

   **Completing todos** (complete_todo):
   - "I finished X"
   - "mark X as done"
   - "X is complete"
   - "check off X"
   - "done with X"

   **Deleting todos** (delete_todo):
   - "remove X"
   - "delete X"
   - "get rid of X"
   - "I don't need X anymore"

   **Updating todos** (update_todo):
   - "change X to Y"
   - "rename X to Y"
   - "update the description of X"
   - "modify task X"
   - "edit the details of X"
   - "add more information to X"

6. **Use tools proactively**: Don't just describe what you'll do - call the appropriate tool immediately.

7. **Provide summaries**: When listing todos, summarize the results:
   - "You have 5 tasks: 3 pending and 2 completed."

8. **Stay focused**: Your primary job is todo management. Politely redirect off-topic requests:
   - "I'm here to help with your todos. Is there a task you'd like to add or manage?"

Remember: You only see todos for the authenticated user. All operations are automatically scoped to their data.
"""


class AssistantConfig:
    """Configuration for OpenAI Assistant."""

    @property
    def assistant_id(self) -> str:
        """Get OpenAI Assistant ID from environment."""
        return settings.openai_assistant_id

    @property
    def instructions(self) -> str:
        """Get assistant instructions."""
        return ASSISTANT_INSTRUCTIONS

    @property
    def model(self) -> str:
        """Get model to use for assistant (if creating programmatically)."""
        return "gpt-4-turbo-preview"

    @property
    def tools(self) -> list:
        """Get tool definitions for assistant (for programmatic creation).

        Note: In production, tools should be registered via OpenAI dashboard
        or API when creating the assistant. This is provided for reference.
        """
        return [
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
                                "description": "Todo title (1-200 characters)",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed description (0-2000 characters)",
                            },
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_todos",
                    "description": "List user's todos, optionally filtered by completion status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed": {
                                "type": "boolean",
                                "description": "Filter by completion status: true for completed, false for pending, omit for all",
                            },
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_todo",
                    "description": "Mark a todo as completed",
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
            },
            {
                "type": "function",
                "function": {
                    "name": "update_todo",
                    "description": "Update a todo's title, description, or completion status",
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
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_todo",
                    "description": "Delete a todo permanently",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "todo_id": {
                                "type": "integer",
                                "description": "ID of the todo to delete",
                            },
                        },
                        "required": ["todo_id"],
                    },
                },
            },
        ]


# Global config instance
assistant_config = AssistantConfig()
