"""Google Gemini API client wrapper for AI assistant functionality."""

import asyncio
from typing import Any, Dict, List, Optional

import structlog
import google.generativeai as genai
from google.generativeai import protos
from google.generativeai.types import GenerationConfig
from google.api_core.exceptions import NotFound, ResourceExhausted

from src.config import settings
from src.ai.assistant_config import ASSISTANT_INSTRUCTIONS

logger = structlog.get_logger(__name__)

TYPE_MAPPING = {
    "string": protos.Type.STRING,
    "number": protos.Type.NUMBER,
    "integer": protos.Type.INTEGER,
    "boolean": protos.Type.BOOLEAN,
    "array": protos.Type.ARRAY,
    "object": protos.Type.OBJECT,
}

class GeminiClient:
    """Async wrapper for Google Gemini API operations."""

    # Model preference order (each model has separate quota)
    MODEL_PREFERENCES = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash-001",
        "gemini-2.5-pro",
    ]

    def __init__(self) -> None:
        """Initialize Gemini client with automatic model detection."""
        genai.configure(api_key=settings.google_api_key)

        # Default to gemini-2.0-flash (current stable model)
        self.model_name = "gemini-2.0-flash"
        self.available_models: List[str] = []
        self.exhausted_models: set = set()  # Track rate-limited models
        self.current_model_index = 0

        try:
            # Try to find models that support text generation
            all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            logger.info("available_gemini_models", models=all_models[:5] if all_models else [])

            # Build ordered list of available models based on preferences
            for preferred in self.MODEL_PREFERENCES:
                match = next((m for m in all_models if m.endswith(preferred)), None)
                if match:
                    self.available_models.append(match)

            # Add any remaining non-experimental models not in preferences
            for m in all_models:
                if m not in self.available_models and '-exp' not in m:
                    self.available_models.append(m)

            if self.available_models:
                self.model_name = self.available_models[0]

            logger.info("ordered_model_fallbacks", models=self.available_models)

            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=ASSISTANT_INSTRUCTIONS
            )
            logger.info("gemini_client_initialized", model=self.model_name)

        except Exception as e:
            logger.error("gemini_discovery_failed", error=str(e))
            # Hardcoded emergency fallback to stable model
            self.model_name = "gemini-2.0-flash"
            self.available_models = ["gemini-2.0-flash"]
            self.model = genai.GenerativeModel(self.model_name)

    def _switch_to_next_model(self) -> bool:
        """Switch to next available model when current one hits rate limits.

        Returns:
            True if switched successfully, False if no more models available.
        """
        self.exhausted_models.add(self.model_name)

        # Find next model not in exhausted set
        for model in self.available_models:
            if model not in self.exhausted_models:
                self.model_name = model
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=ASSISTANT_INSTRUCTIONS
                )
                logger.info("switched_to_fallback_model", model=self.model_name,
                           exhausted=list(self.exhausted_models))
                return True

        logger.warning("all_models_exhausted", exhausted=list(self.exhausted_models))
        return False

    def _get_gemini_type(self, type_str: str) -> protos.Type:
        return TYPE_MAPPING.get(str(type_str).lower(), protos.Type.STRING)

    def _convert_property_to_schema(self, prop_data: Dict[str, Any]) -> protos.Schema:
        prop_type = prop_data.get("type", "string")
        schema_kwargs = {"type": self._get_gemini_type(prop_type)}
        if "description" in prop_data:
            schema_kwargs["description"] = prop_data["description"]
        if prop_type == "array" and "items" in prop_data:
            schema_kwargs["items"] = self._convert_property_to_schema(prop_data["items"])
        if prop_type == "object" and "properties" in prop_data:
            nested_props = {k: self._convert_property_to_schema(v) for k, v in prop_data["properties"].items()}
            schema_kwargs["properties"] = nested_props
            if "required" in prop_data:
                schema_kwargs["required"] = prop_data["required"]
        return protos.Schema(**schema_kwargs)

    def _convert_tools_to_gemini_format(self, tools: List[Dict[str, Any]]) -> List[protos.Tool]:
        function_declarations = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                params = func.get("parameters", {})
                properties = {k: self._convert_property_to_schema(v) for k, v in params.get("properties", {}).items()}
                schema = protos.Schema(type=protos.Type.OBJECT, properties=properties, required=params.get("required"))
                function_declarations.append(protos.FunctionDeclaration(
                    name=func["name"], description=func["description"], parameters=schema))
        return [protos.Tool(function_declarations=function_declarations)] if function_declarations else []

    def _format_conversation_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        history = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if not content or role == "system": continue
            history.append({"role": "model" if role == "assistant" else "user", "parts": [{"text": content}]})
        return history

    async def send_message(self, message: str, conversation_history: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        history = self._format_conversation_history(conversation_history)
        gemini_tools = self._convert_tools_to_gemini_format(tools) if tools else None

        # Try with current model, fallback to others on rate limit
        last_error = None
        while True:
            chat = self.model.start_chat(history=history)
            try:
                response = await asyncio.to_thread(chat.send_message, message, tools=gemini_tools)
                candidate = response.candidates[0]
                text_response = "".join([p.text for p in candidate.content.parts if hasattr(p, 'text')])
                function_calls = [{"name": p.function_call.name, "args": dict(p.function_call.args)}
                                 for p in candidate.content.parts if hasattr(p, 'function_call') and p.function_call]
                # Return chat session for function call continuation
                return {"response": text_response or None, "function_calls": function_calls, "finish_reason": "STOP", "chat": chat}
            except ResourceExhausted as e:
                logger.warning("model_rate_limited", model=self.model_name, error=str(e)[:100])
                last_error = e
                # Try switching to next model
                if not self._switch_to_next_model():
                    # No more models available, raise the error
                    logger.error("gemini_send_failed", error=str(e))
                    raise
                # Continue loop with new model
            except Exception as e:
                logger.error("gemini_send_failed", error=str(e))
                raise

    async def submit_function_results(self, conversation_history: List[Dict[str, str]], function_responses: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, chat: Optional[Any] = None) -> Dict[str, Any]:
        parts = [protos.Part(function_response=protos.FunctionResponse(name=r["name"], response={"result": str(r["response"])})) for r in function_responses]
        gemini_tools = self._convert_tools_to_gemini_format(tools) if tools else None

        # Try with current model, fallback to others on rate limit
        while True:
            # Use existing chat session if provided, otherwise create new one
            if chat is None:
                history = self._format_conversation_history(conversation_history)
                chat = self.model.start_chat(history=history)

            try:
                response = await asyncio.to_thread(chat.send_message, parts, tools=gemini_tools)
                candidate = response.candidates[0]
                text_res = "".join([p.text for p in candidate.content.parts if hasattr(p, 'text')]) or "Done."
                function_calls = [{"name": p.function_call.name, "args": dict(p.function_call.args)}
                                 for p in candidate.content.parts if hasattr(p, 'function_call') and p.function_call]
                return {"response": text_res, "function_calls": function_calls, "finish_reason": "STOP", "chat": chat}
            except ResourceExhausted as e:
                logger.warning("model_rate_limited", model=self.model_name, error=str(e)[:100])
                # Try switching to next model
                if not self._switch_to_next_model():
                    logger.error("gemini_submit_failed", error=str(e))
                    raise
                chat = None  # Reset chat to create new one with new model
            except Exception as e:
                logger.error("gemini_submit_failed", error=str(e))
                raise
