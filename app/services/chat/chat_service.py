"""
Chat orchestrator service — coordinating sessions, messages, and AI interaction.
"""

from __future__ import annotations

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.messages import Message
from app.services.chat.session_service import session_service
from app.services.chat.message_service import message_service
from app.services.chat.ai_service import ai_service

logger = structlog.get_logger(__name__)


class ChatService:
    """
    Orchestrates the chat flow: user sends a message -> AI responds.
    """

    async def process_user_message(
        self,
        db: AsyncSession,
        *,
        session_id: UUID,
        user_id: UUID,
        message_text: str,
    ) -> Message:
        """
        Main entry point for processing a new user message.
        1. Saves the user message.
        2. Generates a session title if it's the first message.
        3. Generates and saves an AI response.
        """
        
        # 1. Save User Message
        user_message = await message_service.create_message(
            db,
            session_id=session_id,
            sender_user_id=user_id,
            sender_type="user",
            message_text=message_text,
        )
        
        logger.debug(
            "user_message_persisted",
            chat_session_id=str(session_id),
            message_id=str(user_message.message_id),
            sequence_number=user_message.sequence_number,
        )

        # 2. Check if we need to auto-generate a session title
        # Only do this if the session still has the default "New Chat" title
        session = await session_service.get_session_for_user(db, session_id, user_id)
        if session.session_title == "New Chat":
            try:
                new_title = await ai_service.generate_title(message_text)
                if new_title:
                    from app.schemas.chat import ChatSessionUpdate
                    await session_service.update_session(
                        db,
                        session_id=session_id,
                        user_id=user_id,
                        obj_in=ChatSessionUpdate(session_title=new_title),
                    )
            except Exception as e:
                logger.warning("failed_to_generate_session_title", error=str(e))

        # 3. Generate AI response (Placeholder for now)
        # In the next step, this will call a real LLM service
        try:
            ai_response_text = await ai_service.generate_reply(message_text)
        except Exception as e:
            logger.error("ai_generation_failed", error=str(e))
            ai_response_text = "I'm sorry, I encountered an error while processing your request. Please try again later."

        # 4. Save AI Message
        ai_message = await message_service.create_message(
            db,
            session_id=session_id,
            sender_user_id=None,  # AI messages have no sender_user_id
            sender_type="ai",
            message_text=ai_response_text,
        )

        logger.info(
            "chat_turn_completed",
            chat_session_id=str(session_id),
            user_message_id=str(user_message.message_id),
            ai_message_id=str(ai_message.message_id),
        )

        return ai_message


chat_service = ChatService()
