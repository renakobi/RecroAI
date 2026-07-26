from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App Settings
    APP_NAME: str = "RecroAI API"
    DEBUG: bool = True

    # 🔹 LLM / AI Settings
    LLM_PROVIDER: str = "openai"  # openai | openrouter
    OPENAI_API_KEY: Optional[str] = None
    
    # OpenRouter settings
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: Optional[str] = None
    
    # Used for BOTH OpenAI and OpenRouter
    LLM_MODEL: Optional[str] = None  # Can override OPENAI_MODEL
    OPENAI_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",   # ← THIS fixes the crash
    )


settings = Settings()
