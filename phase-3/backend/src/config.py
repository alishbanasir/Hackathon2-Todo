"""Configuration management using Pydantic Settings.

Loads environment variables from .env file and provides typed configuration access.
"""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string (shared with Phase 2)",
    )

    # Authentication (Phase 2 compatibility)
    # TEMPORARILY HARD-CODED to bypass .env loading issues
    better_auth_secret: str = Field(
        default="b2d97d33f825d9fd93f22f239ad1181473f7140ddd548c060109fef0f1b93024",
        description="JWT secret key (must match Phase 2)",
    )

    # OpenAI Configuration (DEPRECATED - keeping temporarily for rollback)
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for Assistants API (deprecated)",
    )
    openai_assistant_id: str = Field(
        default="",
        description="OpenAI Assistant ID for todo chatbot (deprecated)",
    )

    # Google Gemini Configuration
    google_api_key: str = Field(
        ...,
        description="Google AI API key for Gemini models",
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use (gemini-1.5-pro or gemini-1.5-flash)",
    )
    gemini_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model temperature for response creativity (0.0-2.0)",
    )
    gemini_max_tokens: int = Field(
        default=2048,
        ge=256,
        le=8192,
        description="Maximum tokens in model response",
    )

    # Application Settings
    app_env: str = Field(
        default="development",
        description="Application environment (development, staging, production)",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3001,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Server Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8001, description="API server port")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
