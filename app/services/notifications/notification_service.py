"""
Notification service — business logic & integration point for in-app notifications.

Other modules should call ``notification_service.send(...)`` to create
notifications for a user.  This keeps the coupling in one place.
"""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import Notification
from app.repositories.notification_repository import notification_repository
from app.schemas.notifications import NotificationType

logger = structlog.get_logger(__name__)


class NotificationService:
    """
    High-level notification operations.

    Other services should use :meth:`send` to push notifications.
    """

    # ── Integration helper (used by other modules) ─────────────────────

    async def send(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        title: str,
        body: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
    ) -> Notification:
        """
        Create and persist a new notification for a user.

        This is the **primary entry point** for other modules:

            await notification_service.send(
                db,
                user_id=user.user_id,
                title="Welcome!",
                body="Your account has been created.",
                notification_type=NotificationType.AUTH,
            )
        """
        notif = await notification_repository.create(
            db,
            obj_in={
                "user_id": user_id,
                "title": title,
                "body": body,
                "notification_type": notification_type.value,
            },
        )
        logger.info(
            "notification_sent",
            notification_id=str(notif.notification_id),
            user_id=str(user_id),
            notification_type=notification_type.value,
            title=title,
        )
        return notif

    # ── List ───────────────────────────────────────────────────────────

    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Notification]:
        """Return a page of notifications for a user, newest first."""
        return await notification_repository.get_by_user_id(
            db,
            user_id,
            is_read=is_read,
            notification_type=notification_type,
            skip=skip,
            limit=limit,
        )

    # ── Counts ─────────────────────────────────────────────────────────

    async def count_total(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: str | None = None,
    ) -> int:
        return await notification_repository.count_for_user(
            db,
            user_id,
            is_read=is_read,
            notification_type=notification_type,
        )

    async def get_unread_count(self, db: AsyncSession, user_id: UUID) -> int:
        return await notification_repository.unread_count(db, user_id)

    # ── Mark as read ───────────────────────────────────────────────────

    async def mark_as_read(
        self, db: AsyncSession, *, notification_id: UUID, user_id: UUID
    ) -> Notification | None:
        """
        Mark a single notification as read.

        Returns the updated notification, or ``None`` if not found / not owned.
        """
        notif = await notification_repository.get_by_id_for_user(
            db, notification_id, user_id
        )
        if notif is None:
            logger.warning(
                "notification_not_found",
                notification_id=str(notification_id),
                user_id=str(user_id),
            )
            return None

        if notif.is_read:
            logger.debug(
                "notification_already_read",
                notification_id=str(notification_id),
            )
            return notif

        updated = await notification_repository.mark_as_read(db, db_obj=notif)
        logger.info(
            "notification_marked_read",
            notification_id=str(notification_id),
            user_id=str(user_id),
        )
        return updated

    async def mark_all_as_read(self, db: AsyncSession, user_id: UUID) -> int:
        """
        Bulk-mark every unread notification for a user.

        Returns the number of notifications that were updated.
        """
        count = await notification_repository.mark_all_as_read(db, user_id)
        logger.info(
            "notifications_bulk_marked_read",
            user_id=str(user_id),
            marked_count=count,
        )
        return count


notification_service = NotificationService()
