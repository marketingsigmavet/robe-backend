"""
Notification repository — database queries for the ``notifications`` table.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification, Any, Any]):
    def __init__(self) -> None:
        super().__init__(Notification)

    # ── Create ─────────────────────────────────────────────────────────

    async def create(
        self, db: AsyncSession, *, obj_in: dict[str, Any]
    ) -> Notification:
        return await super().create(db, obj_in=obj_in)

    # ── Read (single) ──────────────────────────────────────────────────

    async def get_by_id(
        self, db: AsyncSession, notification_id: UUID
    ) -> Notification | None:
        return await db.get(Notification, notification_id)

    async def get_by_id_for_user(
        self, db: AsyncSession, notification_id: UUID, user_id: UUID
    ) -> Notification | None:
        """Fetch a single notification ensuring it belongs to the given user."""
        stmt = select(Notification).where(
            Notification.notification_id == notification_id,
            Notification.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    # ── Read (list) ────────────────────────────────────────────────────

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Notification]:
        """
        Fetch notifications for a user with optional filters.

        Results are ordered newest-first.
        """
        stmt = select(Notification).where(Notification.user_id == user_id)

        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
        if notification_type is not None:
            stmt = stmt.where(Notification.notification_type == notification_type)

        stmt = stmt.order_by(Notification.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    # ── Counts ─────────────────────────────────────────────────────────

    async def count_for_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: str | None = None,
    ) -> int:
        """Return the total number of matching notifications for a user."""
        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id
        )
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
        if notification_type is not None:
            stmt = stmt.where(Notification.notification_type == notification_type)

        result = await db.execute(stmt)
        return result.scalar_one()

    async def unread_count(self, db: AsyncSession, user_id: UUID) -> int:
        """Shortcut for badge display."""
        return await self.count_for_user(db, user_id, is_read=False)

    # ── Update ─────────────────────────────────────────────────────────

    async def mark_as_read(
        self, db: AsyncSession, *, db_obj: Notification
    ) -> Notification:
        """Mark a single notification as read with a timestamp."""
        db_obj.is_read = True
        db_obj.read_at = datetime.now(timezone.utc)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def mark_all_as_read(self, db: AsyncSession, user_id: UUID) -> int:
        """
        Bulk-mark all unread notifications for a user as read.

        Returns the number of rows affected.
        """
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount  # type: ignore[return-value]

    # ── Delete ─────────────────────────────────────────────────────────

    async def delete(
        self, db: AsyncSession, *, id: Any
    ) -> Notification | None:
        return await super().delete(db, id=id)


notification_repository = NotificationRepository()
