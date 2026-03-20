from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.topics import Topic
from app.repositories.base import BaseRepository


class TopicRepository(BaseRepository[Topic, Any, Any]):
    def __init__(self):
        super().__init__(Topic)

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Topic:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> Topic | None:
        return await super().get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[Topic]:
        return await super().get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: Topic, obj_in: dict[str, Any]) -> Topic:
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> Topic | None:
        return await super().delete(db, id=id)

    async def get_active_topics(self, db: AsyncSession) -> Sequence[Topic]:
        # Using getattr to allow safe execution even if is_active is missing
        if hasattr(Topic, "is_active"):
            stmt = select(Topic).where(Topic.is_active == True)
        else:
            stmt = select(Topic)
        result = await db.execute(stmt)
        return result.scalars().all()


topic_repository = TopicRepository()
