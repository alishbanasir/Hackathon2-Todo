"""Google Gemini API client wrapper for AI assistant functionality."""

import asyncio
from typing import Any, Dict, List, Optional

import structlog
import google.generativeai as genai
from google.generativeai import protos
from google.generativeai.types import GenerationConfig
from google.api_core.exceptions import NotFound

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

    def __init__(self) -> None:
        """Initialize Gemini client with automatic model detection."""
        genai.configure(api_key=settings.google_api_key)

        # Default to gemini-1.5-flash (current working model)
        self.model_name = "gemini-1.5-flash"

        try:
            # Try to find models that support text generation
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            logger.info("available_gemini_models", models=available_models[:5] if available_models else [])

            if available_models:
                # Prefer stable models over experimental ones
                # Use exact suffix match to avoid matching gemini-2.0-flash-exp when looking for gemini-2.0-flash
                for preferred in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
                    # Exact suffix match (model names are like "models/gemini-2.0-flash")
                    match = next((m for m in available_models if m.endswith(preferred)), None)
                    if match:
                        self.model_name = match
                        break
                else:
                    # Fallback: pick first non-exp model, or first available
                    non_exp = [m for m in available_models if '-exp' not in m]
                    self.model_name = non_exp[0] if non_exp else available_models[0]

            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=ASSISTANT_INSTRUCTIONS
            )
            logger.info("gemini_client_initialized", model=self.model_name)

        except Exception as e:
            logger.error("gemini_discovery_failed", error=str(e))
            # Hardcoded emergency fallback to working model
            self.model_name = "gemini-1.5-flash"
            self.model = genai.GenerativeModel(self.model_name)

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
        chat = self.model.start_chat(history=history)
        
        try:
            response = await asyncio.to_thread(chat.send_message, message, tools=gemini_tools)
            candidate = response.candidates[0]
            text_response = "".join([p.text for p in candidate.content.parts if hasattr(p, 'text')])
            function_calls = [{"name": p.function_call.name, "args": dict(p.function_call.args)} 
                             for p in candidate.content.parts if hasattr(p, 'function_call') and p.function_call]
            return {"response": text_response or None, "function_calls": function_calls, "finish_reason": "STOP"}
        except Exception as e:
            logger.error("gemini_send_failed", error=str(e))
            raise

    async def submit_function_results(self, conversation_history: List[Dict[str, str]], function_responses: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        history = self._format_conversation_history(conversation_history)
        chat = self.model.start_chat(history=history)
        parts = [protos.Part(function_response=protos.FunctionResponse(name=r["name"], response={"result": str(r["response"])})) for r in function_responses]
        response = await asyncio.to_thread(chat.send_message, parts, tools=self._convert_tools_to_gemini_format(tools) if tools else None)
        candidate = response.candidates[0]
        text_res = "".join([p.text for p in candidate.content.parts if hasattr(p, 'text')]) or "Done."
        return {"response": text_res, "function_calls": [], "finish_reason": "STOP"}
