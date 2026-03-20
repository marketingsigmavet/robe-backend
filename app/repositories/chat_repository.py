from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_sessions import ChatSession
from app.models.messages import Message
from app.repositories.base import BaseRepository


class ChatSessionRepository(BaseRepository[ChatSession, Any, Any]):
    def __init__(self):
        super().__init__(ChatSession)

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ChatSession:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> ChatSession | None:
        return await super().get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[ChatSession]:
        return await super().get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: ChatSession, obj_in: dict[str, Any]) -> ChatSession:
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> ChatSession | None:
        return await super().delete(db, id=id)

    async def get_by_user_id(self, db: AsyncSession, user_id: Any) -> Sequence[ChatSession]:
        # Utilizing user_id if it exists
        stmt = select(ChatSession).where(ChatSession.user_id == user_id)
        if hasattr(ChatSession, "created_at"):
            stmt = stmt.order_by(ChatSession.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()


class MessageRepository(BaseRepository[Message, Any, Any]):
    def __init__(self):
        super().__init__(Message)

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Message:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> Message | None:
        return await super().get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[Message]:
        return await super().get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: Message, obj_in: dict[str, Any]) -> Message:
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> Message | None:
        return await super().delete(db, id=id)

    async def get_by_session_id(self, db: AsyncSession, session_id: Any) -> Sequence[Message]:
        stmt = select(Message).where(Message.session_id == session_id)
        if hasattr(Message, "created_at"):
            stmt = stmt.order_by(Message.created_at.asc())
        result = await db.execute(stmt)
        return result.scalars().all()


chat_session_repository = ChatSessionRepository()
message_repository = MessageRepository()
