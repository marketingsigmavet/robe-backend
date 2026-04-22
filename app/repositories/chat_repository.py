"""Chat repository — handling sessions and messages."""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_sessions import ChatSession
from app.models.messages import Message
from app.repositories.base import BaseRepository


class ChatSessionRepository(BaseRepository[ChatSession, Any, Any]):
    def __init__(self) -> None:
        super().__init__(ChatSession)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        is_archived: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[ChatSession]:
        """Fetch chat sessions for a user, ordered by last activity."""
        stmt = select(ChatSession).where(
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False  # noqa: E712
        )

        if is_archived is not None:
            stmt = stmt.where(ChatSession.is_archived == is_archived)

        # Order by last_message_at (if exists) or started_at
        stmt = stmt.order_by(
            desc(func.coalesce(ChatSession.last_message_at, ChatSession.started_at))
        )
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def count_for_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        is_archived: bool | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.is_deleted == False  # noqa: E712
            )
        )
        if is_archived is not None:
            stmt = stmt.where(ChatSession.is_archived == is_archived)
            
        result = await db.execute(stmt)
        return result.scalar_one()

    async def get_for_user(
        self, db: AsyncSession, session_id: UUID, user_id: UUID
    ) -> ChatSession | None:
        """Fetch a single session ensuring it belongs to the given user."""
        stmt = select(ChatSession).where(
            ChatSession.chat_session_id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False  # noqa: E712
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


class MessageRepository(BaseRepository[Message, Any, Any]):
    def __init__(self) -> None:
        super().__init__(Message)

    async def get_by_session_id(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Message]:
        """Fetch messages for a session, ordered chronologically."""
        stmt = (
            select(Message)
            .where(Message.chat_session_id == session_id)
            .order_by(Message.sequence_number.asc(), Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


chat_session_repository = ChatSessionRepository()
message_repository = MessageRepository()
