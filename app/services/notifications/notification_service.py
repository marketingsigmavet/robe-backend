from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notifications import Notification
from app.repositories.notification_repository import notification_repository


class NotificationService:
    async def create_notification(self, db: AsyncSession, *, notif_in: dict[str, Any]) -> Notification:
        return await notification_repository.create(db, obj_in=notif_in)

    async def get_user_notifications(self, db: AsyncSession, user_id: Any) -> Sequence[Notification]:
        return await notification_repository.get_by_user_id(db, user_id)

    async def mark_as_read(self, db: AsyncSession, *, db_obj: Notification) -> Notification:
        return await notification_repository.mark_as_read(db, db_obj=db_obj)


notification_service = NotificationService()
