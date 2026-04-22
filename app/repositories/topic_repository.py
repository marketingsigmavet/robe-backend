"""Topic repository."""

from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topics import Topic
from app.repositories.base import BaseRepository


class TopicRepository(BaseRepository[Topic, Any, Any]):
    def __init__(self) -> None:
        super().__init__(Topic)

    async def get_by_slug(
        self, db: AsyncSession, slug: str
    ) -> Topic | None:
        stmt = select(Topic).where(
            Topic.slug == slug,
            Topic.is_deleted == False,  # noqa: E712
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(
        self, db: AsyncSession
    ) -> Sequence[Topic]:
        """Active, non-deleted topics ordered by sort_order (user-facing)."""
        stmt = (
            select(Topic)
            .where(
                Topic.is_active == True,  # noqa: E712
                Topic.is_deleted == False,  # noqa: E712
            )
            .order_by(Topic.sort_order, Topic.topic_name)
        )
        result = await db.execute(stmt)
        return result.scalars().unique().all()


topic_repository = TopicRepository()
