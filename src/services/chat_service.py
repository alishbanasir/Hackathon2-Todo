"""ChatService for AI assistant conversation management.

Handles Google Gemini API integration, tool call execution,
and conversation persistence.
"""

import asyncio
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.gemini_client import GeminiClient
from src.mcp.tool_registry import ToolRegistry
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.repositories.conversation_repository import ConversationRepository
from src.repositories.message_repository import MessageRepository

logger = structlog.get_logger(__name__)


class ChatService:
    """Service for processing chat messages through AI assistant.

    Manages conversation flow:
    1. Create or load conversation (no thread - conversation_id only)
    2. Load message history from database
    3. Add user message to database
    4. Send to Gemini with history and tools
    5. Handle function calls with user context injection
    6. Save assistant response to database
    7. Return conversation with assistant message
    """

    def __init__(
        self,
        session: AsyncSession,
        gemini_client: GeminiClient,
    ) -> None:
        """Initialize ChatService.

        Args:
            session: Database session for conversation/message persistence
            gemini_client: Gemini API client
        """
        self.session = session
        self.gemini_client = gemini_client
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)
        self.tool_registry = ToolRegistry(session)

    async def process_message(
        self,
        message_content: str,
        user_id: UUID,
        conversation_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Process a chat message and return assistant response (FR-016, FR-017).

        Args:
            message_content: User's message text
            user_id: Authenticated user ID from JWT (FR-015)
            conversation_id: Optional existing conversation ID (FR-019, FR-020)

        Returns:
            Dictionary with conversation_id, assistant message, and metadata

        Raises:
            ValueError: If conversation_id invalid or doesn't belong to user
            Exception: If OpenAI API or database operation fails
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Step 1: Get or create conversation (FR-019, FR-020)
            conversation = await self._get_or_create_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
            )

            logger.info(
                "chat_processing_started",
                user_id=str(user_id),
                conversation_id=str(conversation.id),
                message_length=len(message_content),
            )

            # Step 2: Load conversation history from database (NEW)
            conversation_history = await self._load_conversation_history(
                conversation_id=conversation.id
            )

            # Step 3: Save user message to database (FR-018)
            user_message = await self._save_user_message(
                conversation_id=conversation.id,
                content=message_content,
            )

            # Step 4: Run assistant with Gemini and handle tool calls (FR-016, FR-017)
            assistant_response = await self._run_assistant_with_tools(
                message=message_content,
                conversation_history=conversation_history,
                user_id=user_id,
            )

            # Step 5: Save assistant message to database (FR-018)
            assistant_message = await self._save_assistant_message(
                conversation_id=conversation.id,
                content=assistant_response,
            )

            # Step 6: Update conversation last_message_at timestamp
            await self.conversation_repo.update_last_message_at(conversation.id)
            await self.session.commit()

            # Calculate processing time
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000

            logger.info(
                "chat_processing_completed",
                user_id=str(user_id),
                conversation_id=str(conversation.id),
                duration_ms=round(duration_ms, 2),
                assistant_response_length=len(assistant_response),
            )

            return {
                "conversation_id": str(conversation.id),
                "message": assistant_response,
                "user_message_id": str(user_message.id),
                "assistant_message_id": str(assistant_message.id),
                "processing_time_ms": round(duration_ms, 2),
            }

        except Exception as e:
            logger.error(
                "chat_processing_failed",
                user_id=str(user_id),
                conversation_id=str(conversation_id) if conversation_id else None,
                error=str(e),
                exc_info=True,
            )
            raise

    async def _get_or_create_conversation(
        self,
        user_id: UUID,
        conversation_id: Optional[UUID],
    ) -> Conversation:
        """Get existing conversation or create new one (FR-019, FR-020).

        Args:
            user_id: User ID for ownership verification
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation instance

        Raises:
            ValueError: If conversation doesn't exist or doesn't belong to user (FR-032)
        """
        if conversation_id:
            # Load existing conversation (FR-019)
            conversation = await self.conversation_repo.get_by_id(conversation_id)

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Verify ownership (FR-032, FR-039)
            if conversation.user_id != user_id:
                raise ValueError(
                    "Unauthorized: Conversation does not belong to user"
                )

            logger.info(
                "conversation_loaded",
                conversation_id=str(conversation_id),
                user_id=str(user_id),
            )

            return conversation

        else:
            # Create new conversation (no thread needed for Gemini) (FR-020)
            conversation = Conversation(
                user_id=user_id,
                openai_thread_id="",  # DEPRECATED: Set to empty string
            )

            conversation = await self.conversation_repo.create(conversation)
            await self.session.flush()

            logger.info(
                "conversation_created",
                conversation_id=str(conversation.id),
                user_id=str(user_id),
            )

            return conversation

    async def _save_user_message(
        self,
        conversation_id: UUID,
        content: str,
    ) -> Message:
        """Save user message to database (FR-018).

        Args:
            conversation_id: Conversation ID
            content: Message content

        Returns:
            Created Message instance
        """
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=content,
        )

        message = await self.message_repo.create(message)
        await self.session.flush()

        return message

    async def _save_assistant_message(
        self,
        conversation_id: UUID,
        content: str,
    ) -> Message:
        """Save assistant message to database (FR-018).

        Args:
            conversation_id: Conversation ID
            content: Message content

        Returns:
            Created Message instance
        """
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=content,
        )

        message = await self.message_repo.create(message)
        await self.session.flush()

        return message

    async def _load_conversation_history(
        self,
        conversation_id: UUID,
    ) -> List[Dict[str, str]]:
        """Load conversation message history from database (NEW METHOD).

        Args:
            conversation_id: Conversation ID

        Returns:
            List of message dicts with 'role' and 'content'

        Example:
            [
                {"role": "user", "content": "Add buy groceries"},
                {"role": "assistant", "content": "I've added..."},
                {"role": "user", "content": "Show my todos"}
            ]
        """
        # Get all messages for conversation, ordered by created_at
        messages = await self.message_repo.get_by_conversation_id(
            conversation_id=conversation_id,
            limit=50,  # Limit history to last 50 messages for context window
        )

        history = []
        for msg in messages:
            history.append({
                "role": msg.role.value,  # "user" or "assistant"
                "content": msg.content,
            })

        logger.info(
            "conversation_history_loaded",
            conversation_id=str(conversation_id),
            message_count=len(history),
        )

        return history

    async def _run_assistant_with_tools(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        user_id: UUID,
        max_retries: int = 3,
    ) -> str:
        """Run assistant with Gemini and handle tool calls (FR-036).

        Args:
            message: Current user message
            conversation_history: Prior conversation messages
            user_id: User ID for tool execution context (FR-015, FR-030, FR-031)
            max_retries: Maximum retry attempts for failures (default 3)

        Returns:
            Assistant's text response

        Raises:
            Exception: If assistant run fails after retries (FR-036)
        """
        for attempt in range(max_retries):
            try:
                # Get MCP tools in OpenAI format (will be converted by GeminiClient)
                tools = self.tool_registry.to_openai_functions()

                # Send message with history and tools
                response = await self.gemini_client.send_message(
                    message=message,
                    conversation_history=conversation_history,
                    tools=tools,
                )

                # Handle function calls if present (FR-033)
                if response["function_calls"]:
                    return await self._handle_function_calls(
                        function_calls=response["function_calls"],
                        conversation_history=conversation_history,
                        user_id=user_id,
                        tools=tools,
                        chat=response.get("chat"),
                    )

                # Return text response
                return response["response"] or "I encountered an issue. Please try again."

            except Exception as e:
                logger.error(
                    "assistant_run_error",
                    error=str(e),
                    attempt=attempt + 1,
                    exc_info=True,
                )

                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return "I'm experiencing technical difficulties. Please try again later."

        return "I'm experiencing technical difficulties. Please try again later."

    async def _handle_function_calls(
        self,
        function_calls: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]],
        user_id: UUID,
        tools: List[Dict[str, Any]],
        chat: Optional[Any] = None,
    ) -> str:
        """Handle function calls from Gemini (FR-033).

        Args:
            function_calls: List of function calls from Gemini
            conversation_history: Current conversation history
            user_id: User ID for tool execution context (FR-015, FR-030, FR-031)
            tools: MCP tools for continued function calling
            chat: Active Gemini chat session for function response continuation

        Returns:
            Final assistant response after executing functions
        """
        function_responses = []

        for func_call in function_calls:
            tool_name = func_call["name"]
            tool_args = func_call["args"]

            logger.info(
                "function_call_received",
                tool_name=tool_name,
                user_id=str(user_id),
            )

            # Get tool from registry
            tool = self.tool_registry.get_tool(tool_name)

            if not tool:
                logger.warning(
                    "tool_not_found",
                    tool_name=tool_name,
                )
                function_responses.append({
                    "name": tool_name,
                    "response": {
                        "success": False,
                        "error": "tool_not_found",
                        "message": "Tool not available"
                    },
                })
                continue

            # Execute tool with user_id injection (FR-015, FR-030, FR-031)
            try:
                result = await tool.execute(
                    parameters=tool_args,
                    user_id=user_id,  # User isolation enforcement
                )

                logger.info(
                    "function_executed",
                    tool_name=tool_name,
                    user_id=str(user_id),
                    success=result.get("success", False),
                )

                function_responses.append({
                    "name": tool_name,
                    "response": result,
                })

            except Exception as e:
                logger.error(
                    "function_execution_failed",
                    tool_name=tool_name,
                    user_id=str(user_id),
                    error=str(e),
                    exc_info=True,
                )

                function_responses.append({
                    "name": tool_name,
                    "response": {
                        "success": False,
                        "error": "execution_error",
                        "message": "Tool execution failed"
                    },
                })

        # Submit function results back to Gemini (pass chat session to maintain context)
        final_response = await self.gemini_client.submit_function_results(
            conversation_history=conversation_history,
            function_responses=function_responses,
            tools=tools,
            chat=chat,
        )

        # Handle cascading function calls (recursive)
        if final_response["function_calls"]:
            logger.warning(
                "cascading_function_calls_detected",
                count=len(final_response["function_calls"]),
            )
            return await self._handle_function_calls(
                function_calls=final_response["function_calls"],
                conversation_history=conversation_history,
                user_id=user_id,
                tools=tools,
                chat=final_response.get("chat"),
            )

        return final_response["response"] or "I've completed that action."
