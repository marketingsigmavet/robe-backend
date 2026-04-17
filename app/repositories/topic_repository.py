from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.topics import Topic
from app.repositories.base import BaseRepository
from app.schemas.topics import TopicCreate, TopicUpdate


class TopicRepository(BaseRepository[Topic, TopicCreate, TopicUpdate]):
    def __init__(self):
        super().__init__(Topic)

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Topic | None:
        stmt = select(Topic).where(Topic.slug == slug, Topic.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().first()



    async def get_active_topics(self, db: AsyncSession) -> Sequence[Topic]:
        # Using getattr to allow safe execution even if is_active is missing
        if hasattr(Topic, "is_active"):
            stmt = select(Topic).where(Topic.is_active == True)
        else:
            stmt = select(Topic)
        result = await db.execute(stmt)
        return result.scalars().all()


topic_repository = TopicRepository()
