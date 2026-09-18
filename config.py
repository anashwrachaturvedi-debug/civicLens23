"""Application configuration.

Centralizes all environment-driven settings using Pydantic Settings.
Every other module that needs configuration (database URL, JWT secrets,
mail credentials, CORS origins, etc.) imports the single ``settings``
instance defined here rather than reading environment variables directly.
"""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "CivicLens AI"
    ENV: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = Field(
        ...,
        description="Async SQLAlchemy connection string, e.g. postgresql+asyncpg://user:pass@host:5432/db",
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False

    # --- Security / JWT ---
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_REFRESH_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # --- CORS ---
    CORS_ORIGINS: list[AnyHttpUrl] = []
    CORS_ALLOW_CREDENTIALS: bool = True

    # --- Mail ---
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: EmailStr | None = None
    MAIL_FROM_NAME: str = "CivicLens AI"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # --- AI Model ---
    AI_MODEL_PATH: str = "app/ai_models/yolov8_civiclens.pt"
    AI_CONFIDENCE_THRESHOLD: float = 0.4
    AI_DEVICE: Literal["cpu", "cuda"] = "cpu"

    # --- File Uploads ---
    UPLOAD_DIR: str = "app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

    # --- Rate Limiting ---
    RATE_LIMIT_PER_MINUTE: int = 60

    # --- Logging ---
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_DIR: str = "logs"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Allow CORS_ORIGINS to be provided as a comma-separated string."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        """Return True when running in the production environment."""
        return self.ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached, process-wide singleton of application settings."""
    return Settings()


settings: Settings = get_settings()