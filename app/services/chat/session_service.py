from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_sessions import ChatSession
from app.repositories.chat_repository import chat_session_repository


class SessionService:
    async def create_session(self, db: AsyncSession, *, session_in: dict[str, Any]) -> ChatSession:
        return await chat_session_repository.create(db, obj_in=session_in)

    async def get_session(self, db: AsyncSession, session_id: Any) -> ChatSession | None:
        return await chat_session_repository.get(db, session_id)

    async def get_user_sessions(self, db: AsyncSession, user_id: Any) -> Sequence[ChatSession]:
        return await chat_session_repository.get_by_user_id(db, user_id)

    async def archive_session(self, db: AsyncSession, *, db_obj: ChatSession) -> ChatSession:
        return await chat_session_repository.update(db, db_obj=db_obj, obj_in={"is_archived": True})


session_service = SessionService()
