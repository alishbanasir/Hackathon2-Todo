from pydantic_settings import BaseSettings

class AssistantConfig(BaseSettings):
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 2048

    class Config:
        env_prefix = "ASSISTANT_"

assistant_config = AssistantConfig()
