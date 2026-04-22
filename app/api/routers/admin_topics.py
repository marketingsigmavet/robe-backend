"""
Admin topic & question endpoints — full CRUD (requires admin role).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import RoleChecker
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.topics import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    TopicCreate,
    TopicResponse,
    TopicUpdate,
)
from app.services.topics.question_service import question_service
from app.services.topics.topic_service import topic_service

router = APIRouter()
admin_required = RoleChecker(["admin"])


# ═══════════════════════════════════════════════════════════════════════════
# Topics
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=list[TopicResponse])
async def list_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """List all topics (admin view — includes inactive)."""
    return await topic_service.get_all_topics(db, skip=skip, limit=limit)


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get a single topic with all its questions."""
    return await topic_service.get_topic(db, topic_id)


@router.post("/", response_model=TopicResponse, status_code=201)
async def create_topic(
    payload: TopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Create a new topic."""
    return await topic_service.create_topic(db, obj_in=payload)


@router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: uuid.UUID,
    payload: TopicUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Update a topic."""
    return await topic_service.update_topic(
        db, topic_id=topic_id, obj_in=payload
    )


@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Soft-delete a topic."""
    await topic_service.delete_topic(db, topic_id=topic_id)
    return {"status": "deleted"}


# ═══════════════════════════════════════════════════════════════════════════
# Questions (nested under topics)
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/{topic_id}/questions",
    response_model=list[QuestionResponse],
)
async def list_questions(
    topic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """List all questions under a topic (includes inactive)."""
    # Validate topic exists
    await topic_service.get_topic(db, topic_id)
    return await question_service.get_questions(db, topic_id)


@router.post(
    "/{topic_id}/questions",
    response_model=QuestionResponse,
    status_code=201,
)
async def create_question(
    topic_id: uuid.UUID,
    payload: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Create a new question under a topic."""
    # Validate topic exists
    await topic_service.get_topic(db, topic_id)
    return await question_service.create_question(
        db, topic_id=topic_id, obj_in=payload
    )


@router.get(
    "/{topic_id}/questions/{question_id}",
    response_model=QuestionResponse,
)
async def get_question(
    topic_id: uuid.UUID,
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get a single question."""
    return await question_service.get_question(db, question_id)


@router.patch(
    "/{topic_id}/questions/{question_id}",
    response_model=QuestionResponse,
)
async def update_question(
    topic_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Update a question."""
    return await question_service.update_question(
        db, question_id=question_id, obj_in=payload
    )


@router.delete("/{topic_id}/questions/{question_id}")
async def delete_question(
    topic_id: uuid.UUID,
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Soft-delete a question."""
    await question_service.delete_question(db, question_id=question_id)
    return {"status": "deleted"}
