from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.chat.session_service import session_service
from app.services.chat.message_service import message_service


class ChatService:
    """
    High-level orchestrator for chat session lifecycles.
    """
    async def initiate_chat(self, db: AsyncSession, user_id: Any, topic_id: Any) -> Any:
        # High-level orchestration stub
        return await session_service.create_session(db, session_in={"user_id": user_id, "topic_id": topic_id})


chat_service = ChatService()
