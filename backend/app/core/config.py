from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    PROJECT_NAME: str = "LegalFlow AI"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://legalflow_user:legalflow_password_secret@postgres:5432/legalflow_db"
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql://legalflow_user:legalflow_password_secret@postgres:5432/legalflow_db"
    )

    # Security settings
    JWT_SECRET_KEY: str = Field(
        default="change_this_to_a_secure_random_key_in_production_32_bytes_min"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Services
    AI_SERVICE_URL: str = "http://ai-service:8001"
    RAG_SERVICE_URL: str = "http://rag-service:8002"
    BACKEND_WEBHOOK_SECRET: str = "webhook_secret_key_legalflow_2026"

    # Storage
    STORAGE_PATH: str = "./data/storage"


settings = Settings()
