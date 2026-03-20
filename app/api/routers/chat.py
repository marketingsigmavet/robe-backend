from typing import Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.services.chat.chat_service import chat_service
from app.services.chat.session_service import session_service
from app.services.chat.message_service import message_service

router = APIRouter()

@router.post("/sessions")
async def create_chat_session(
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("user_id", "stub-id")
    topic_id = payload.get("topic_id")
    return await chat_service.initiate_chat(db, user_id=user_id, topic_id=topic_id)

@router.get("/sessions/{id}")
async def get_chat_session(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    return await session_service.get_session(db, id)

@router.post("/sessions/{id}/messages")
async def send_message(
    id: str,
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    # Stub message creation endpoint
    payload["session_id"] = id
    return await message_service.create_message(db, message_in=payload)
