"""Message service — managing chat messages."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.messages import Message
from app.repositories.chat_repository import message_repository

logger = structlog.get_logger(__name__)


class MessageService:
    async def create_message(
        self,
        db: AsyncSession,
        *,
        session_id: UUID,
        sender_user_id: UUID | None,
        sender_type: str,
        message_text: str,
        message_type: str = "text",
        metadata: dict | None = None,
    ) -> Message:
        """
        Create a new message in a session.
        Handles sequence number calculation and session timestamp updates.
        """
        # Determine sequence number atomically (within session context)
        stmt = select(func.max(Message.sequence_number)).where(
            Message.chat_session_id == session_id
        )
        result = await db.execute(stmt)
        max_seq = result.scalar() or 0
        sequence_number = max_seq + 1

        obj_in = {
            "chat_session_id": session_id,
            "sender_user_id": sender_user_id,
            "sender_type": sender_type,
            "message_text": message_text,
            "message_type": message_type,
            "message_metadata": metadata,
            "sequence_number": sequence_number,
        }
        
        message = await message_repository.create(db, obj_in=obj_in)
        
        # Update session's last_message_at
        from app.repositories.chat_repository import chat_session_repository
        session = await chat_session_repository.get(db, session_id)
        if session:
            await chat_session_repository.update(
                db, 
                db_obj=session, 
                obj_in={"last_message_at": message.created_at}
            )
        
        logger.debug(
            "message_created",
            message_id=str(message.message_id),
            session_id=str(session_id),
            sender_type=sender_type,
            sequence=sequence_number,
        )
            
        return message

    async def get_messages_for_session(
        self, 
        db: AsyncSession, 
        session_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Message]:
        """Fetch chronological message history for a session."""
        return await message_repository.get_by_session_id(
            db, session_id, skip=skip, limit=limit
        )


message_service = MessageService()
