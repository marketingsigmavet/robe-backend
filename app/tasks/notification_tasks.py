"""
Background tasks for notification delivery (Push, In-app).
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import structlog
from celery import shared_task

from app.db.session import get_sessionmaker

logger = structlog.get_logger(__name__)


@shared_task(name="app.tasks.notification_tasks.deliver_notification_task")
def deliver_notification_task(notification_id: str) -> None:
    """
    Background task to process a notification (e.g., send push or email).
    """
    asyncio.run(_deliver_notification(UUID(notification_id)))


async def _deliver_notification(notification_id: UUID) -> None:
    # This is a placeholder for actual external delivery logic (Firebase, AWS SNS, etc.)
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        try:
            # Here we would fetch the notification and send it to the user's devices
            logger.info(
                "notification_delivered_background",
                notification_id=str(notification_id),
            )
            # Mark as delivered in DB if tracking status
            # await db.commit()
        except Exception as e:
            logger.error(
                "notification_delivery_failed",
                notification_id=str(notification_id),
                error=str(e),
            )
