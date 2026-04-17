from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import RoleChecker
from app.schemas.topics import TopicResponse, TopicCreate, TopicUpdate
from app.services.topics.topic_service import topic_service
from app.models.users import User

router = APIRouter()

@router.get("/", response_model=List[TopicResponse])
async def list_topics(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await topic_service.get_all_topics(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=TopicResponse)
async def get_topic(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await topic_service.get_topic(db, id)


@router.post("/", response_model=TopicResponse)
async def create_topic(
    payload: TopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await topic_service.create_topic(db, obj_in=payload)


@router.patch("/{id}", response_model=TopicResponse)
async def update_topic(
    id: str,
    payload: TopicUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await topic_service.update_topic(db, topic_id=id, obj_in=payload)


@router.delete("/{id}")
async def delete_topic(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    await topic_service.delete_topic(db, topic_id=id)
    return {"status": "deleted"}
