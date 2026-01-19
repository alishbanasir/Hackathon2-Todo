"""AI integration components for Google Gemini API.

Provides async wrappers for chat session management and function calling.
"""

from src.ai.assistant_config import AssistantConfig
from src.ai.gemini_client import GeminiClient

__all__ = ["AssistantConfig", "GeminiClient"]
