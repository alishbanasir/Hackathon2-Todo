"""OpenAI Assistants API client wrapper.

Provides async methods for thread management, message sending, and run execution.
"""

import asyncio
from typing import Any, Dict, List, Optional

import structlog
from openai import AsyncOpenAI
from openai.types.beta.threads import Run

from src.config import settings

logger = structlog.get_logger(__name__)


class OpenAIClient:
    """Async wrapper for OpenAI Assistants API operations.

    Handles thread creation, message sending, and assistant run execution
    with proper error handling and logging.
    """

    def __init__(self) -> None:
        """Initialize OpenAI async client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.assistant_id = settings.openai_assistant_id

    async def create_thread(self) -> str:
        """Create a new OpenAI thread for conversation context.

        Returns:
            Thread ID string

        Raises:
            OpenAIError: If thread creation fails
        """
        try:
            thread = await self.client.beta.threads.create()
            logger.info("openai_thread_created", thread_id=thread.id)
            return thread.id
        except Exception as e:
            logger.error("openai_thread_creation_failed", error=str(e))
            raise

    async def add_message(
        self,
        thread_id: str,
        content: str,
        role: str = "user",
    ) -> str:
        """Add a message to a thread.

        Args:
            thread_id: OpenAI thread ID
            content: Message text content
            role: Message role (default "user")

        Returns:
            Message ID string

        Raises:
            OpenAIError: If message creation fails
        """
        try:
            message = await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=content,
            )
            logger.info(
                "openai_message_added",
                thread_id=thread_id,
                message_id=message.id,
                role=role,
            )
            return message.id
        except Exception as e:
            logger.error(
                "openai_message_creation_failed",
                thread_id=thread_id,
                error=str(e),
            )
            raise

    async def run_assistant(
        self,
        thread_id: str,
        additional_instructions: Optional[str] = None,
    ) -> Run:
        """Run the assistant on a thread and wait for completion.

        Args:
            thread_id: OpenAI thread ID
            additional_instructions: Optional instructions to append to assistant

        Returns:
            Run object with status and results

        Raises:
            OpenAIError: If run creation or execution fails
            TimeoutError: If run exceeds 30 second timeout
        """
        try:
            # Create and start run
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                additional_instructions=additional_instructions,
            )

            logger.info(
                "openai_run_started",
                thread_id=thread_id,
                run_id=run.id,
            )

            # Poll for completion with timeout
            max_attempts = 30  # 30 seconds max
            for attempt in range(max_attempts):
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id,
                )

                if run.status in ["completed", "failed", "cancelled", "expired"]:
                    logger.info(
                        "openai_run_finished",
                        thread_id=thread_id,
                        run_id=run.id,
                        status=run.status,
                    )
                    return run

                if run.status == "requires_action":
                    # Tool calls needed - return run for caller to handle
                    logger.info(
                        "openai_run_requires_action",
                        thread_id=thread_id,
                        run_id=run.id,
                    )
                    return run

                # Wait before next poll
                await asyncio.sleep(1)

            # Timeout reached
            logger.error(
                "openai_run_timeout",
                thread_id=thread_id,
                run_id=run.id,
            )
            raise TimeoutError(f"Assistant run timed out after {max_attempts} seconds")

        except TimeoutError:
            raise
        except Exception as e:
            logger.error(
                "openai_run_failed",
                thread_id=thread_id,
                error=str(e),
            )
            raise

    async def submit_tool_outputs(
        self,
        thread_id: str,
        run_id: str,
        tool_outputs: List[Dict[str, Any]],
    ) -> Run:
        """Submit tool call outputs and continue run.

        Args:
            thread_id: OpenAI thread ID
            run_id: Run ID
            tool_outputs: List of tool outputs with call_id and output

        Returns:
            Updated Run object

        Raises:
            OpenAIError: If submission fails
        """
        try:
            run = await self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs,
            )

            logger.info(
                "openai_tool_outputs_submitted",
                thread_id=thread_id,
                run_id=run_id,
                tool_count=len(tool_outputs),
            )

            # Wait for completion after tool outputs
            max_attempts = 30
            for attempt in range(max_attempts):
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id,
                )

                if run.status in ["completed", "failed", "cancelled", "expired"]:
                    return run

                await asyncio.sleep(1)

            raise TimeoutError("Run timed out after tool submission")

        except Exception as e:
            logger.error(
                "openai_tool_submission_failed",
                thread_id=thread_id,
                run_id=run_id,
                error=str(e),
            )
            raise

    async def get_latest_message(self, thread_id: str) -> Optional[str]:
        """Get the latest assistant message from a thread.

        Args:
            thread_id: OpenAI thread ID

        Returns:
            Latest assistant message content, or None if no messages

        Raises:
            OpenAIError: If retrieval fails
        """
        try:
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=1,
                order="desc",
            )

            if not messages.data:
                return None

            latest_message = messages.data[0]
            if latest_message.role == "assistant" and latest_message.content:
                # Extract text from content blocks
                for content_block in latest_message.content:
                    if hasattr(content_block, "text"):
                        return content_block.text.value

            return None

        except Exception as e:
            logger.error(
                "openai_message_retrieval_failed",
                thread_id=thread_id,
                error=str(e),
            )
            raise
