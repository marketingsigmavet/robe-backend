"""
Celery configuration and app instance.
"""

from __future__ import annotations

import structlog
from celery import Celery
from celery.signals import setup_logging, worker_process_init

from app.core.config import get_settings
from app.db.session import init_engine

settings = get_settings()
logger = structlog.get_logger(__name__)

# Create the celery app
celery_app = Celery(
    "robe_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.chat_tasks",
        "app.tasks.notification_tasks",
    ],
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
)

@setup_logging.connect
def config_loggers(*args, **kwtags):
    """
    Ensure Celery worker uses our structured logging configuration.
    """
    from app.core.logging import configure_logging
    settings = get_settings()
    configure_logging(
        level=settings.log_level,
        json_output=settings.is_aws,
        environment=settings.app_env.value,
    )


@worker_process_init.connect
def init_worker(**kwargs):
    """
    Initialize database engine when a worker process starts.
    """
    settings = get_settings()
    init_engine(settings.database_url)
    logger.info("worker_process_db_engine_initialised")


if __name__ == "__main__":
    celery_app.start()
