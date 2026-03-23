from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="RoBe Backend", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    version: str = Field(default="0.1.0")

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Database (async SQLAlchemy)
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    # Redis
    redis_url: str = Field("redis://localhost:6379/0", validation_alias="REDIS_URL")

    # Celery
    celery_broker_url: str = Field(
        "redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        "redis://localhost:6379/0",
        validation_alias="CELERY_RESULT_BACKEND",
    )

    # JWT
    jwt_secret: str = Field(default="super-secret-key-change-me-in-production", validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 7) # 7 days
    
    # OTP
    otp_expire_seconds: int = Field(default=300) # 5 minutes
    otp_max_attempts: int = Field(default=5)
    otp_resend_cooldown_seconds: int = Field(default=60)
    debug_mode: bool = Field(default=False, validation_alias="DEBUG_MODE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def get_redis_url() -> str:
    return get_settings().redis_url

