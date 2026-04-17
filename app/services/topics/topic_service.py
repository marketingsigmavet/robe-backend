from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.topics import Topic
from app.repositories.topic_repository import topic_repository
from app.schemas.topics import TopicCreate, TopicUpdate


class TopicService:
    async def get_all_topics(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Topic]:
        return await topic_repository.get_multi(db, skip=skip, limit=limit)

    async def get_active_topics(self, db: AsyncSession) -> Sequence[Topic]:
        return await topic_repository.get_active_topics(db)

    async def get_topic(self, db: AsyncSession, topic_id: Any) -> Topic:
        topic = await topic_repository.get(db, topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic

    async def create_topic(self, db: AsyncSession, *, obj_in: TopicCreate) -> Topic:
        if await topic_repository.get_by_slug(db, obj_in.slug):
            raise HTTPException(status_code=400, detail="Topic with this slug already exists")
        return await topic_repository.create(db, obj_in=obj_in)

    async def update_topic(self, db: AsyncSession, *, topic_id: Any, obj_in: TopicUpdate) -> Topic:
        topic = await self.get_topic(db, topic_id)
        # Check slug uniqueness if changed
        if obj_in.slug and obj_in.slug != topic.slug:
            if await topic_repository.get_by_slug(db, obj_in.slug):
                raise HTTPException(status_code=400, detail="Topic with this slug already exists")
        return await topic_repository.update(db, db_obj=topic, obj_in=obj_in)

    async def delete_topic(self, db: AsyncSession, *, topic_id: Any) -> Topic:
        topic = await self.get_topic(db, topic_id)
        # Note: Soft deletion handles foreign keys securely natively
        return await topic_repository.delete(db, id=topic_id)


topic_service = TopicService()
