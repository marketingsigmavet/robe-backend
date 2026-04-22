"""
Chat router — managing chat sessions and messages.

Endpoints
---------
POST   /chat/sessions          – start a new chat session
GET    /chat/sessions          – list current user's chat sessions
GET    /chat/sessions/{id}     – get session details
PATCH  /chat/sessions/{id}     – update session (title, archive)
DELETE /chat/sessions/{id}     – delete session
GET    /chat/sessions/{id}/messages – get message history
POST   /chat/sessions/{id}/messages – send a new message
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionListResponse,
    ChatSessionResponse,
    ChatSessionSummary,
    ChatSessionUpdate,
    MessageCreate,
    MessageResponse,
)
from app.services.chat.chat_service import chat_service
from app.services.chat.session_service import session_service
from app.services.chat.message_service import message_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Session Management
# ---------------------------------------------------------------------------

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start a new chat session linked to topic, question, pet or personality."""
    # Note: In a fully implemented chat_service.initiate_chat might handle 
    # more logic like initial AI message, but for now we use session_service
    return await session_service.create_session(db, user_id=current_user.user_id, session_in=payload)


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(
    is_archived: bool | None = Query(None, description="Filter by archived status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List current user's chat sessions, newest active first."""
    sessions = await session_service.get_user_sessions(
        db, user_id=current_user.user_id, is_archived=is_archived, skip=skip, limit=limit
    )
    total = await session_service.count_user_sessions(
        db, user_id=current_user.user_id, is_archived=is_archived
    )
    return ChatSessionListResponse(
        sessions=[ChatSessionSummary.model_validate(s) for s in sessions],
        total=total,
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed info about a specific chat session."""
    return await session_service.get_session_for_user(
        db, session_id=session_id, user_id=current_user.user_id
    )


@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: uuid.UUID,
    payload: ChatSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update session title or toggle archived status."""
    return await session_service.update_session(
        db, session_id=session_id, user_id=current_user.user_id, obj_in=payload
    )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Soft-delete a chat session."""
    await session_service.delete_session(db, session_id=session_id, user_id=current_user.user_id)
    return {"status": "deleted"}


# ---------------------------------------------------------------------------
# Message Management
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    session_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get chronological message history for a session."""
    # Ensure session exists and belongs to user
    await session_service.get_session_for_user(db, session_id, current_user.user_id)
    return await message_service.get_messages_for_session(db, session_id=session_id, skip=skip, limit=limit)


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: uuid.UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Send a new message in the chat session and get AI response."""
    # Ensure session exists and belongs to user
    await session_service.get_session_for_user(db, session_id, current_user.user_id)
    
    return await chat_service.process_user_message(
        db, 
        session_id=session_id, 
        user_id=current_user.user_id, 
        message_text=payload.message_text
    )
