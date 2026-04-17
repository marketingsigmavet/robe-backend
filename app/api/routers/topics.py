from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user
from app.models.users import User
from app.schemas.topics import TopicResponse
from app.services.topics.topic_service import topic_service

router = APIRouter()

@router.get("/", response_model=List[TopicResponse])
async def list_topics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await topic_service.get_active_topics(db)

@router.get("/{id}", response_model=TopicResponse)
async def get_topic(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await topic_service.get_topic(db, id)
