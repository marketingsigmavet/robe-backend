"""
User-facing topic & question endpoints — read-only, active only.

Users browse topics and their questions, then use a question to start
a new AI chat session.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.topics import (
    QuestionSummary,
    TopicDetailResponse,
    TopicSummary,
)
from app.services.topics.question_service import question_service
from app.services.topics.topic_service import topic_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[TopicSummary])
async def list_topics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active topics with their active questions."""
    topics = await topic_service.get_active_topics(db)
    results = []
    for t in topics:
        active_questions = [q for q in t.questions if q.is_active and not q.is_deleted]
        results.append(
            TopicSummary(
                topic_id=t.topic_id,
                topic_name=t.topic_name,
                slug=t.slug,
                description=t.description,
                icon_url=t.icon_url,
                sort_order=t.sort_order,
                questions=[QuestionSummary.model_validate(q) for q in active_questions],
            )
        )
    return results


@router.get("/{topic_id}", response_model=TopicDetailResponse)
async def get_topic(
    topic_id: uuid.UUID,
    species_id: uuid.UUID | None = Query(None, description="Filter questions by species"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a topic with its questions.

    Optionally filter questions by ``species_id`` to show only questions
    relevant to the user's pet type.
    """
    topic = await topic_service.get_topic_for_user(db, topic_id)
    questions = await question_service.get_questions_for_user(
        db, topic.topic_id, species_id=species_id
    )
    return TopicDetailResponse(
        topic_id=topic.topic_id,
        topic_name=topic.topic_name,
        slug=topic.slug,
        description=topic.description,
        icon_url=topic.icon_url,
        sort_order=topic.sort_order,
        questions=[QuestionSummary.model_validate(q) for q in questions],
    )


# ---------------------------------------------------------------------------
# Questions — direct access
# ---------------------------------------------------------------------------

@router.get(
    "/{topic_id}/questions",
    response_model=list[QuestionSummary],
)
async def list_questions(
    topic_id: uuid.UUID,
    species_id: uuid.UUID | None = Query(None, description="Filter by species"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active questions under a topic."""
    questions = await question_service.get_questions_for_user(
        db, topic_id, species_id=species_id
    )
    return [QuestionSummary.model_validate(q) for q in questions]
