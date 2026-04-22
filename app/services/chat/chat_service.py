"""
Chat orchestrator service — coordinating sessions, messages, and background AI interaction.
"""

from __future__ import annotations

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.messages import Message
from app.services.chat.session_service import session_service
from app.services.chat.message_service import message_service
from app.tasks.chat_tasks import generate_ai_reply_task, generate_session_title_task

logger = structlog.get_logger(__name__)


class ChatService:
    """
    Orchestrates the chat flow using background tasks for heavy computations.
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
        Processes a new user message:
        1. Saves the user message synchronously (to provide immediate feedback).
        2. Offloads title generation and AI response to Celery.
        """
        
        # 1. Save User Message Synchronously
        user_message = await message_service.create_message(
            db,
            session_id=session_id,
            sender_user_id=user_id,
            sender_type="user",
            message_text=message_text,
        )
        
        logger.info(
            "user_message_persisted",
            chat_session_id=str(session_id),
            message_id=str(user_message.message_id),
        )

        # 2. Check if we need to auto-generate a session title
        session = await session_service.get_session_for_user(db, session_id, user_id)
        if session.session_title == "New Chat":
            generate_session_title_task.delay(
                str(session_id), str(user_id), message_text
            )

        # 3. Offload AI response generation to background task
        generate_ai_reply_task.delay(str(session_id), message_text)

        logger.info(
            "chat_turn_delegated_to_background",
            chat_session_id=str(session_id),
        )

        return user_message


chat_service = ChatService()
