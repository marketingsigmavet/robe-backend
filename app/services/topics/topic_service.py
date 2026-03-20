from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.topics import Topic
from app.repositories.topic_repository import topic_repository


class TopicService:
    async def get_active_topics(self, db: AsyncSession) -> Sequence[Topic]:
        return await topic_repository.get_active_topics(db)

    async def get_topic(self, db: AsyncSession, topic_id: Any) -> Topic | None:
        return await topic_repository.get(db, topic_id)


topic_service = TopicService()
