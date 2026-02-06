"""Groq API client wrapper for AI assistant functionality.

Replaces Google Gemini with Groq (free tier, generous limits, function calling support).
Maintains the same GeminiClient class name to avoid changing imports elsewhere.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional

import structlog
from groq import Groq

from src.config import settings
from src.ai.assistant_config import ASSISTANT_INSTRUCTIONS

logger = structlog.get_logger(__name__)

# Model to use — llama-3.3-70b-versatile has excellent function calling support
GROQ_MODEL = "llama-3.3-70b-versatile"


class GeminiClient:
    """Async wrapper for Groq API operations.

    Named GeminiClient to maintain backward compatibility with existing imports.
    """

    def __init__(self) -> None:
        """Initialize Groq client."""
        self.client = Groq(api_key=settings.groq_api_key)
        self.model_name = GROQ_MODEL
        logger.info("groq_client_initialized", model=self.model_name)

    def _convert_tools_to_openai_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tools from tool_registry.to_openai_functions() are already in OpenAI format.

        Groq uses the same format, so just pass through.
        """
        return tools if tools else []

    def _format_conversation_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert conversation history to OpenAI message format."""
        history = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if not content:
                continue
            # Map roles: keep user/assistant as-is, skip system (handled separately)
            if role == "system":
                continue
            history.append({"role": role, "content": content})
        return history

    async def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send a message to Groq and get a response.

        Args:
            message: The user's message
            conversation_history: Prior conversation messages
            tools: Optional tool definitions in OpenAI format

        Returns:
            Dict with 'response', 'function_calls', and 'finish_reason'
        """
        # Build messages list
        messages = [{"role": "system", "content": ASSISTANT_INSTRUCTIONS}]
        messages.extend(self._format_conversation_history(conversation_history))
        messages.append({"role": "user", "content": message})

        # Build API call kwargs
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        groq_tools = self._convert_tools_to_openai_format(tools)
        if groq_tools:
            kwargs["tools"] = groq_tools
            kwargs["tool_choice"] = "auto"

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create, **kwargs
            )

            choice = response.choices[0]
            text_response = choice.message.content or ""

            # Extract function calls if any
            function_calls = []
            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                    function_calls.append({
                        "name": tc.function.name,
                        "args": args,
                    })

            logger.info(
                "groq_send_success",
                model=self.model_name,
                has_function_calls=bool(function_calls),
                response_length=len(text_response),
            )

            return {
                "response": text_response or None,
                "function_calls": function_calls,
                "finish_reason": choice.finish_reason,
            }

        except Exception as e:
            logger.error("groq_send_failed", error=str(e))
            raise

    async def submit_function_results(
        self,
        conversation_history: List[Dict[str, str]],
        function_responses: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Submit function call results back to Groq for final response.

        Args:
            conversation_history: Prior conversation messages
            function_responses: Results from executed functions
            tools: Tool definitions for potential cascading calls

        Returns:
            Dict with 'response', 'function_calls', and 'finish_reason'
        """
        # Build messages with function results
        messages = [{"role": "system", "content": ASSISTANT_INSTRUCTIONS}]
        messages.extend(self._format_conversation_history(conversation_history))

        # Add tool results as tool messages
        for func_resp in function_responses:
            # First add the assistant's tool call (required by API)
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": f"call_{func_resp['name']}",
                    "type": "function",
                    "function": {
                        "name": func_resp["name"],
                        "arguments": "{}",
                    },
                }],
            })
            # Then add the tool response
            messages.append({
                "role": "tool",
                "tool_call_id": f"call_{func_resp['name']}",
                "content": json.dumps(func_resp["response"]),
            })

        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        groq_tools = self._convert_tools_to_openai_format(tools)
        if groq_tools:
            kwargs["tools"] = groq_tools

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create, **kwargs
            )

            choice = response.choices[0]
            text_response = choice.message.content or "Done."

            # Check for cascading function calls
            function_calls = []
            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                    function_calls.append({
                        "name": tc.function.name,
                        "args": args,
                    })

            return {
                "response": text_response,
                "function_calls": function_calls,
                "finish_reason": choice.finish_reason,
            }

        except Exception as e:
            logger.error("groq_submit_results_failed", error=str(e))
            raise
