from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.messages import Message
from app.repositories.chat_repository import message_repository


class MessageService:
    async def create_message(self, db: AsyncSession, *, session_id: Any, sender_user_id: Any | None, sender_type: str, message_text: str) -> Message:
        # Determine sequence number
        stmt = select(func.max(Message.sequence_number)).where(Message.chat_session_id == session_id)
        result = await db.execute(stmt)
        max_seq = result.scalar() or 0
        sequence_number = max_seq + 1

        obj_in = {
            "chat_session_id": session_id,
            "sender_user_id": sender_user_id,
            "sender_type": sender_type,
            "message_text": message_text,
            "message_type": "text",
            "sequence_number": sequence_number
        }
        return await message_repository.create(db, obj_in=obj_in)

    async def get_messages_for_session(self, db: AsyncSession, session_id: Any) -> Sequence[Message]:
        return await message_repository.get_by_session_id(db, session_id)


message_service = MessageService()
