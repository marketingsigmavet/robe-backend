from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user
from app.models.users import User
from app.schemas.chat import ChatSessionCreate, ChatSessionResponse, MessageCreate, MessageResponse
from app.services.chat.chat_service import chat_service
from app.services.chat.session_service import session_service
from app.services.chat.message_service import message_service

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    payload: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await chat_service.initiate_chat(db, user_id=current_user.user_id, session_in=payload)

@router.get("/sessions/{id}", response_model=ChatSessionResponse)
async def get_chat_session(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await session_service.get_session(db, id)

@router.get("/sessions/{id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await message_service.get_messages_for_session(db, session_id=id)

@router.post("/sessions/{id}/messages", response_model=MessageResponse)
async def send_message(
    id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await chat_service.process_user_message(
        db, 
        session_id=id, 
        user_id=current_user.user_id, 
        message_text=payload.message_text
    )
