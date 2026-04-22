"""
Centralised configuration loaded from environment variables.

Environments
------------
- **local**  – Developer laptop; reads from ``.env`` / ``.env.local``.
- **dev**    – AWS shared development account.
- **qa**     – AWS QA / integration-test account.
- **uat**    – AWS pre-production (user acceptance testing).
- **prod**   – AWS production.

For every environment except *local*, the app expects variables to be
injected via the container environment (ECS task-definition, Lambda env,
SSM Parameter Store, or Secrets Manager).  An optional AWS Secrets Manager
integration is provided: set ``AWS_SECRET_NAME`` to a secret ARN/name and
the app will fetch and merge those values at startup.
"""

from __future__ import annotations

import json
import logging
from enum import StrEnum
from functools import lru_cache
from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Environment enum
# ---------------------------------------------------------------------------

class Environment(StrEnum):
    """Supported runtime environments."""

    LOCAL = "local"
    DEV = "dev"
    QA = "qa"
    UAT = "uat"
    PROD = "prod"

    @property
    def is_aws(self) -> bool:
        """Return ``True`` for any cloud-deployed environment."""
        return self is not Environment.LOCAL

    @property
    def is_production(self) -> bool:
        return self is Environment.PROD

    @property
    def is_testing(self) -> bool:
        return self in (Environment.QA, Environment.UAT)


# ---------------------------------------------------------------------------
# Defaults per environment
# ---------------------------------------------------------------------------

_ENV_DEFAULTS: dict[Environment, dict[str, Any]] = {
    Environment.LOCAL: {
        "debug_mode": True,
        "log_level": "DEBUG",
        "cors_origins": ["http://localhost:3000", "http://localhost:5173"],
    },
    Environment.DEV: {
        "debug_mode": True,
        "log_level": "DEBUG",
        "cors_origins": ["https://dev.robe.lk"],
    },
    Environment.QA: {
        "debug_mode": False,
        "log_level": "INFO",
        "cors_origins": ["https://qa.robe.lk"],
    },
    Environment.UAT: {
        "debug_mode": False,
        "log_level": "INFO",
        "cors_origins": ["https://uat.robe.lk"],
    },
    Environment.PROD: {
        "debug_mode": False,
        "log_level": "WARNING",
        "cors_origins": ["https://robe.lk", "https://www.robe.lk"],
    },
}


# ---------------------------------------------------------------------------
# AWS Secrets Manager helper
# ---------------------------------------------------------------------------

def _load_aws_secrets(secret_name: str, region: str) -> dict[str, Any]:
    """
    Fetch a JSON secret from AWS Secrets Manager and return it as a dict.

    Falls back to an empty dict on any error so the app can still start
    with plain environment variables.
    """
    try:
        import boto3  # noqa: WPS433 — deferred import, only needed on AWS

        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString", "{}")
        return json.loads(secret_string)
    except Exception:
        logger.warning(
            "Failed to load secret '%s' from AWS Secrets Manager. "
            "Falling back to environment variables only.",
            secret_name,
            exc_info=True,
        )
        return {}


# ---------------------------------------------------------------------------
# Settings model
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """
    Application configuration.

    Resolution order (highest priority first):
      1. Explicit environment variables
      2. AWS Secrets Manager values (if ``aws_secret_name`` is set)
      3. ``.env`` / ``.env.local`` file (local only)
      4. Field defaults (including per-environment defaults)
    """

    # ── App ────────────────────────────────────────────────────────────
    app_name: str = Field(default="RoBe Backend", validation_alias="APP_NAME")
    app_env: Environment = Field(default=Environment.LOCAL, validation_alias="APP_ENV")
    version: str = Field(default="0.1.0")

    # ── Logging ────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # ── Debug ──────────────────────────────────────────────────────────
    debug_mode: bool = Field(default=False, validation_alias="DEBUG_MODE")

    # ── Database (async SQLAlchemy) ────────────────────────────────────
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    # ── Redis ──────────────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )

    # ── Celery ─────────────────────────────────────────────────────────
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_RESULT_BACKEND",
    )

    # ── JWT / Auth ─────────────────────────────────────────────────────
    jwt_secret: str = Field(
        default="super-secret-key-change-me-in-production",
        validation_alias="JWT_SECRET",
    )
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 7)  # 7 days

    # ── OTP ────────────────────────────────────────────────────────────
    otp_expire_seconds: int = Field(default=300)  # 5 minutes
    otp_max_attempts: int = Field(default=5)
    otp_resend_cooldown_seconds: int = Field(default=60)

    # ── CORS ───────────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias="CORS_ORIGINS",
    )

    # ── AWS (only relevant for non-local environments) ─────────────────
    aws_region: str = Field(default="ap-southeast-1", validation_alias="AWS_REGION")
    aws_secret_name: str | None = Field(default=None, validation_alias="AWS_SECRET_NAME")

    # ── Server ─────────────────────────────────────────────────────────
    server_host: str = Field(default="0.0.0.0", validation_alias="SERVER_HOST")
    server_port: int = Field(default=8000, validation_alias="SERVER_PORT")

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Validators ─────────────────────────────────────────────────────

    @model_validator(mode="before")
    @classmethod
    def _apply_env_defaults_and_secrets(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        1. If running on AWS and ``AWS_SECRET_NAME`` is set, fetch secrets
           and merge them (env-vars still take priority).
        2. Apply per-environment defaults for any field not explicitly set.
        """
        # Normalise the environment value
        raw_env = (
            values.get("APP_ENV")
            or values.get("app_env")
            or "local"
        )
        try:
            env = Environment(str(raw_env).lower())
        except ValueError:
            env = Environment.LOCAL

        # --- AWS Secrets Manager integration ---
        if env.is_aws:
            secret_name = values.get("AWS_SECRET_NAME") or values.get("aws_secret_name")
            region = (
                values.get("AWS_REGION")
                or values.get("aws_region")
                or "ap-southeast-1"
            )
            if secret_name:
                secrets = _load_aws_secrets(secret_name, region)
                # Merge: explicit env-vars beat secrets
                for key, val in secrets.items():
                    upper_key = key.upper()
                    if upper_key not in values and key not in values:
                        values[upper_key] = val

        # --- Per-environment defaults ---
        defaults = _ENV_DEFAULTS.get(env, {})
        for key, default_val in defaults.items():
            upper_key = key.upper()
            if key not in values and upper_key not in values:
                values[key] = default_val

        return values

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """Hard-fail if production is running with the placeholder JWT secret."""
        if self.app_env.is_production and self.jwt_secret == "super-secret-key-change-me-in-production":
            raise ValueError(
                "JWT_SECRET must be set to a secure value in production. "
                "Do not use the default placeholder."
            )
        return self

    # ── Convenience helpers ────────────────────────────────────────────

    @property
    def is_local(self) -> bool:
        return self.app_env == Environment.LOCAL

    @property
    def is_aws(self) -> bool:
        return self.app_env.is_aws

    @property
    def is_production(self) -> bool:
        return self.app_env.is_production


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    settings = Settings()
    logger.info(
        "Configuration loaded — env=%s, debug=%s, log_level=%s",
        settings.app_env.value,
        settings.debug_mode,
        settings.log_level,
    )
    return settings


def get_redis_url() -> str:
    return get_settings().redis_url
