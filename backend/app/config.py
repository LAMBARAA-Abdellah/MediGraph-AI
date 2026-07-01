"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="MediGraph AI", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # OpenAI Compatible LLM
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_api_base: str = Field(
        default="https://api.openai.com/v1", alias="OPENAI_API_BASE"
    )
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # Database
    database_url: str = Field(
        default="sqlite:///./data/medigraph.db", alias="DATABASE_URL"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    use_redis: bool = Field(default=False, alias="USE_REDIS")

    # MCP
    mcp_server_host: str = Field(default="0.0.0.0", alias="MCP_SERVER_HOST")
    mcp_server_port: int = Field(default=8100, alias="MCP_SERVER_PORT")
    mcp_server_url: str = Field(
        default="http://localhost:8100", alias="MCP_SERVER_URL"
    )

    # LangGraph
    langgraph_checkpoint_dir: str = Field(
        default="./data/checkpoints", alias="LANGGRAPH_CHECKPOINT_DIR"
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="./logs/medigraph.log", alias="LOG_FILE")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000", alias="CORS_ORIGINS"
    )

    # Security
    secret_key: str = Field(default="dev-secret-key", alias="SECRET_KEY")

    # Medical disclaimer
    medical_disclaimer: str = Field(
        default="This system does not replace a professional medical consultation.",
        alias="MEDICAL_DISCLAIMER",
    )

    # Diagnostic workflow
    max_questions: int = 5

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton)."""
    return Settings()
