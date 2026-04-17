import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Production AI Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = True

    # Security - Pydantic will automatically override this from environment variable AGENT_API_KEY
    AGENT_API_KEY: str = "demo-secret-key-change-me"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # LLM Config
    OPENAI_API_KEY: str | None = None
    LLM_MODEL: str = "mock-gpt-4o"

    # Redis Config
    REDIS_URL: str = "redis://localhost:6379/0"

    # Guardrails
    RATE_LIMIT_PER_MINUTE: int = 10
    DAILY_BUDGET_USD: float = 1.0

    # Cấu hình ưu tiên đọc từ Environment Variables của Railway
    model_config = SettingsConfigDict(extra="ignore", case_sensitive=True)

settings = Settings()
