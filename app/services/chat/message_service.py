from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.messages import Message
from app.repositories.chat_repository import message_repository


class MessageService:
    async def create_message(self, db: AsyncSession, *, message_in: dict[str, Any]) -> Message:
        return await message_repository.create(db, obj_in=message_in)

    async def get_messages_for_session(self, db: AsyncSession, session_id: Any) -> Sequence[Message]:
        return await message_repository.get_by_session_id(db, session_id)


message_service = MessageService()
