from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notifications import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification, Any, Any]):
    def __init__(self):
        super().__init__(Notification)

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Notification:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> Notification | None:
        return await super().get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[Notification]:
        return await super().get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: Notification, obj_in: dict[str, Any]) -> Notification:
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> Notification | None:
        return await super().delete(db, id=id)

    async def get_by_user_id(self, db: AsyncSession, user_id: Any) -> Sequence[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def mark_as_read(self, db: AsyncSession, *, db_obj: Notification) -> Notification:
        return await self.update(db, db_obj=db_obj, obj_in={"is_read": True})


notification_repository = NotificationRepository()
