"""Topic service — CRUD with structured logging."""

from __future__ import annotations

from typing import Any, Sequence

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topics import Topic
from app.repositories.topic_repository import topic_repository
from app.schemas.topics import TopicCreate, TopicUpdate

logger = structlog.get_logger(__name__)


class TopicService:
    # ── User-facing ────────────────────────────────────────────────────

    async def get_active_topics(self, db: AsyncSession) -> Sequence[Topic]:
        """Return active topics ordered by sort_order (user-facing)."""
        return await topic_repository.get_active(db)

    async def get_topic_for_user(
        self, db: AsyncSession, topic_id: Any
    ) -> Topic:
        topic = await topic_repository.get(db, topic_id)
        if not topic or not topic.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        return topic

    async def get_topic_by_slug(
        self, db: AsyncSession, slug: str
    ) -> Topic:
        topic = await topic_repository.get_by_slug(db, slug)
        if not topic or not topic.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        return topic

    # ── Admin ──────────────────────────────────────────────────────────

    async def get_all_topics(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Topic]:
        return await topic_repository.get_multi(db, skip=skip, limit=limit)

    async def get_topic(self, db: AsyncSession, topic_id: Any) -> Topic:
        topic = await topic_repository.get(db, topic_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        return topic

    async def create_topic(
        self, db: AsyncSession, *, obj_in: TopicCreate
    ) -> Topic:
        if await topic_repository.get_by_slug(db, obj_in.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Topic with this slug already exists",
            )
        topic = await topic_repository.create(db, obj_in=obj_in)
        logger.info(
            "topic_created",
            topic_id=str(topic.topic_id),
            slug=topic.slug,
            topic_name=topic.topic_name,
        )
        return topic

    async def update_topic(
        self, db: AsyncSession, *, topic_id: Any, obj_in: TopicUpdate
    ) -> Topic:
        topic = await self.get_topic(db, topic_id)
        if obj_in.slug and obj_in.slug != topic.slug:
            if await topic_repository.get_by_slug(db, obj_in.slug):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Topic with this slug already exists",
                )
        updated = await topic_repository.update(db, db_obj=topic, obj_in=obj_in)
        logger.info(
            "topic_updated",
            topic_id=str(topic.topic_id),
            slug=updated.slug,
        )
        return updated

    async def delete_topic(
        self, db: AsyncSession, *, topic_id: Any
    ) -> Topic:
        topic = await self.get_topic(db, topic_id)
        deleted = await topic_repository.delete(db, id=topic.topic_id)
        logger.info("topic_deleted", topic_id=str(topic.topic_id))
        return deleted


topic_service = TopicService()
