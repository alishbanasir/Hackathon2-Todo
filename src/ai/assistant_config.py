import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ASSISTANT_INSTRUCTIONS = "You are a professional AI Todo Assistant. Help users manage their tasks effectively."

class AssistantConfig(BaseSettings):
    model_name: str = os.getenv("ASSISTANT_MODEL_NAME", "gemini-1.5-flash")
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 2048

    model_config = SettingsConfigDict(
        env_prefix="ASSISTANT_",
        protected_namespaces=('settings_',),
        extra="ignore"
    )

assistant_config = AssistantConfig()
