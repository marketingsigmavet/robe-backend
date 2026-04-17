from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.chat.session_service import session_service
from app.services.chat.message_service import message_service
from app.services.chat.ai_service import ai_service
from app.schemas.chat import ChatSessionCreate


class ChatService:
    """
    High-level orchestrator for chat session lifecycles.
    """
    async def initiate_chat(self, db: AsyncSession, user_id: Any, session_in: ChatSessionCreate) -> Any:
        return await session_service.create_session(db, user_id=user_id, session_in=session_in)

    async def process_user_message(self, db: AsyncSession, *, session_id: Any, user_id: Any, message_text: str) -> Any:
        # 1. Save User Message
        user_message = await message_service.create_message(
            db, 
            session_id=session_id, 
            sender_user_id=user_id, 
            sender_type="user", 
            message_text=message_text
        )

        # 2. Check if we need to generate title
        if user_message.sequence_number == 1:
            title = await ai_service.generate_title(message_text)
            await session_service.update_session_title(db, session_id=session_id, new_title=title)

        # 3. Ask AI for reply
        ai_reply_text = await ai_service.generate_reply(message_text)

        # 4. Save AI Message
        ai_message = await message_service.create_message(
            db, 
            session_id=session_id, 
            sender_user_id=None, 
            sender_type="ai", 
            message_text=ai_reply_text
        )

        return ai_message


chat_service = ChatService()
