import os
from typing import List

class Settings:
    APP_NAME: str = "Production AI Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    
    # Ép đọc trực tiếp từ os.environ để đảm bảo hoạt động trên Cloud
    AGENT_API_KEY: str = os.environ.get("AGENT_API_KEY", "demo-secret-key-change-me")
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    LLM_MODEL: str = "mock-gpt-4o"
    RATE_LIMIT_PER_MINUTE: int = 10
    DAILY_BUDGET_USD: float = 1.0

settings = Settings()
