from pydantic_settings import BaseSettings

ASSISTANT_INSTRUCTIONS = "You are a professional AI Todo Assistant."

class AssistantConfig(BaseSettings):
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7

    class Config:
        env_prefix = "ASSISTANT_"
        protected_namespaces = ('settings_',)

assistant_config = AssistantConfig()
