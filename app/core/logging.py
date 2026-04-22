"""
Centralised logging configuration using **structlog**.

Design
------
* **Local** environment  → pretty, coloured console output for developers.
* **AWS** environments   → JSON lines for CloudWatch / log aggregators.
* Stdlib ``logging`` is bridged so that *all* libraries (SQLAlchemy, uvicorn,
  celery, etc.) also flow through structlog processors.
* Every log entry automatically includes: ``timestamp``, ``level``,
  ``logger`` (module name), ``environment``, and an optional ``request_id``
  bound via the request middleware.

Usage
-----
In any module::

    import structlog
    logger = structlog.get_logger(__name__)

    logger.info("user_registered", user_id=42, channel="email")
    logger.warning("otp_rate_limited", identifier="+94***1234")
    logger.error("db_connection_failed", exc_info=True)
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def configure_logging(
    level: str = "INFO",
    *,
    json_output: bool = False,
    environment: str = "local",
) -> None:
    """
    Initialise the logging subsystem.  Call once at application startup.

    Parameters
    ----------
    level:
        Root log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    json_output:
        ``True`` → JSON renderer (for CloudWatch / log aggregators).
        ``False`` → coloured console renderer (for local dev).
    environment:
        Current environment name; bound into every log event.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # ── Shared processors (run for every log event) ────────────────────
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,          # request_id etc.
        structlog.stdlib.add_log_level,                   # level key
        structlog.stdlib.add_logger_name,                 # logger key
        structlog.processors.TimeStamper(fmt="iso"),      # timestamp key
        structlog.processors.StackInfoRenderer(),         # stack_info
        structlog.processors.UnicodeDecoder(),            # bytes → str
        _add_environment(environment),                    # environment key
    ]

    if json_output:
        # ── JSON renderer for AWS (CloudWatch, DataDog, ELK, etc.) ────
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        # ── Pretty console renderer for local development ─────────────
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )

    # ── Configure structlog ────────────────────────────────────────────
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # ── Configure stdlib logging (captures uvicorn, sqlalchemy, etc.) ──
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    root_logger = logging.getLogger()
    # Remove any existing handlers to avoid duplicate output
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    # ── Quieten overly chatty libraries ────────────────────────────────
    _set_library_log_levels(numeric_level)


def _set_library_log_levels(app_level: int) -> None:
    """
    Prevent noisy third-party loggers from flooding output at DEBUG.
    """
    quiet_loggers = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.INFO,
        "uvicorn.error": logging.INFO,
        "sqlalchemy.engine": logging.WARNING,
        "sqlalchemy.pool": logging.WARNING,
        "asyncpg": logging.WARNING,
        "celery": logging.INFO,
        "celery.worker": logging.INFO,
        "celery.app.trace": logging.WARNING,
        "redis": logging.WARNING,
        "httpcore": logging.WARNING,
        "httpx": logging.WARNING,
        "boto3": logging.WARNING,
        "botocore": logging.WARNING,
        "s3transfer": logging.WARNING,
        "urllib3": logging.WARNING,
    }
    for name, minimum in quiet_loggers.items():
        logging.getLogger(name).setLevel(max(app_level, minimum))


def _add_environment(environment: str) -> structlog.types.Processor:
    """Return a processor that stamps every event with the environment name."""

    def processor(
        logger: Any, method_name: str, event_dict: dict[str, Any]
    ) -> dict[str, Any]:
        event_dict["environment"] = environment
        return event_dict

    return processor


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Convenience wrapper around ``structlog.get_logger``.

    Usage::

        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("something_happened", detail="value")
    """
    return structlog.get_logger(name)
