import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ASSISTANT_INSTRUCTIONS = "You are a professional AI Todo Assistant."

class AssistantConfig(BaseSettings):
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7

    model_config = SettingsConfigDict(
        env_prefix="ASSISTANT_",
        protected_namespaces=('settings_',),
        extra="ignore"
    )

assistant_config = AssistantConfig()
