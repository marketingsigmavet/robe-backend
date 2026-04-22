"""Chat session service — managing session lifecycle."""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_sessions import ChatSession
from app.repositories.chat_repository import chat_session_repository
from app.schemas.chat import ChatSessionCreate, ChatSessionUpdate

logger = structlog.get_logger(__name__)


class SessionService:
    # ── User-facing ────────────────────────────────────────────────────

    async def create_session(
        self, db: AsyncSession, *, user_id: UUID, session_in: ChatSessionCreate
    ) -> ChatSession:
        """Create a new chat session linked to topic, question, pet or personality."""
        
        # Default title and type
        session_title = "New Chat"
        session_type = "general"
        
        if session_in.is_general_chat:
            session_type = "general"
        elif session_in.topic_id:
            session_type = "topic_discussion"
            # In a real app, we might fetch the topic name here to set as initial title
        elif session_in.question_id:
            session_type = "question_discussion"
        
        obj_in = session_in.model_dump(exclude={"initial_message"})
        obj_in["user_id"] = user_id
        obj_in["session_title"] = session_title
        obj_in["session_type"] = session_type
        
        session = await chat_session_repository.create(db, obj_in=obj_in)
        
        logger.info(
            "chat_session_created",
            chat_session_id=str(session.chat_session_id),
            user_id=str(user_id),
            session_type=session_type,
            topic_id=str(session_in.topic_id) if session_in.topic_id else None,
            question_id=str(session_in.question_id) if session_in.question_id else None,
        )
        return session

    async def get_user_sessions(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        is_archived: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[ChatSession]:
        """Return a page of chat sessions for a user."""
        return await chat_session_repository.get_by_user_id(
            db, user_id, is_archived=is_archived, skip=skip, limit=limit
        )

    async def count_user_sessions(
        self, db: AsyncSession, user_id: UUID, *, is_archived: bool | None = None
    ) -> int:
        return await chat_session_repository.count_for_user(
            db, user_id, is_archived=is_archived
        )

    async def get_session_for_user(
        self, db: AsyncSession, session_id: UUID, user_id: UUID
    ) -> ChatSession:
        """Fetch a single session ensuring it belongs to the user."""
        session = await chat_session_repository.get_for_user(db, session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found",
            )
        return session

    async def update_session(
        self,
        db: AsyncSession,
        *,
        session_id: UUID,
        user_id: UUID,
        obj_in: ChatSessionUpdate,
    ) -> ChatSession:
        """Update session title or archive status."""
        session = await self.get_session_for_user(db, session_id, user_id)
        updated = await chat_session_repository.update(db, db_obj=session, obj_in=obj_in)
        
        logger.info(
            "chat_session_updated",
            chat_session_id=str(session_id),
            user_id=str(user_id),
            fields_updated=list(obj_in.model_dump(exclude_unset=True).keys()),
        )
        return updated

    async def delete_session(
        self, db: AsyncSession, *, session_id: UUID, user_id: UUID
    ) -> ChatSession:
        """Soft-delete a chat session."""
        session = await self.get_session_for_user(db, session_id, user_id)
        deleted = await chat_session_repository.delete(db, id=session.chat_session_id)
        
        logger.info(
            "chat_session_deleted",
            chat_session_id=str(session_id),
            user_id=str(user_id),
        )
        return deleted


session_service = SessionService()
