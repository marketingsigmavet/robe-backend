"""TopicQuestion repository."""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_questions import TopicQuestion
from app.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[TopicQuestion, Any, Any]):
    def __init__(self) -> None:
        super().__init__(TopicQuestion)

    async def get_by_topic(
        self,
        db: AsyncSession,
        topic_id: UUID,
        *,
        active_only: bool = False,
    ) -> Sequence[TopicQuestion]:
        """Return questions for a topic, ordered by sort_order."""
        stmt = select(TopicQuestion).where(
            TopicQuestion.topic_id == topic_id,
            TopicQuestion.is_deleted == False,  # noqa: E712
        )
        if active_only:
            stmt = stmt.where(TopicQuestion.is_active == True)  # noqa: E712
        stmt = stmt.order_by(TopicQuestion.sort_order, TopicQuestion.question_text)
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def get_for_user(
        self,
        db: AsyncSession,
        topic_id: UUID,
        *,
        species_id: UUID | None = None,
    ) -> Sequence[TopicQuestion]:
        """Active questions for a topic, optionally filtered by species tag."""
        stmt = select(TopicQuestion).where(
            TopicQuestion.topic_id == topic_id,
            TopicQuestion.is_active == True,  # noqa: E712
            TopicQuestion.is_deleted == False,  # noqa: E712
        )
        if species_id:
            stmt = stmt.where(
                TopicQuestion.species.any(species_id=species_id)
            )
        stmt = stmt.order_by(TopicQuestion.sort_order)
        result = await db.execute(stmt)
        return result.scalars().unique().all()


question_repository = QuestionRepository()
