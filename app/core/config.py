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

