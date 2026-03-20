from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.services.topics.topic_service import topic_service

router = APIRouter()

@router.get("/")
async def list_topics(
    db: AsyncSession = Depends(get_db)
):
    return await topic_service.get_active_topics(db)

@router.get("/{id}")
async def get_topic(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    return await topic_service.get_topic(db, id)
