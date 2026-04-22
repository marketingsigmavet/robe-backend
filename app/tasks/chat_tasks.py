"""
Background tasks for chat-related operations (AI responses, session titling).
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import structlog
from celery import shared_task

from app.db.session import get_sessionmaker
from app.services.chat.ai_service import ai_service
from app.services.chat.message_service import message_service
from app.services.chat.session_service import session_service

logger = structlog.get_logger(__name__)


@shared_task(name="app.tasks.chat_tasks.generate_ai_reply_task")
def generate_ai_reply_task(session_id: str, user_message_text: str) -> None:
    """
    Background task to generate an AI response and save it to the session.
    """
    asyncio.run(_generate_ai_reply(UUID(session_id), user_message_text))


async def _generate_ai_reply(session_id: UUID, user_message_text: str) -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        try:
            # 1. Generate AI Response
            ai_response_text = await ai_service.generate_reply(user_message_text)
            
            # 2. Save AI Message
            await message_service.create_message(
                db,
                session_id=session_id,
                sender_user_id=None,
                sender_type="ai",
                message_text=ai_response_text,
            )
            
            await db.commit()
            logger.info(
                "ai_reply_generated_background",
                chat_session_id=str(session_id),
            )
        except Exception as e:
            logger.error(
                "ai_generation_task_failed",
                chat_session_id=str(session_id),
                error=str(e),
            )
            # Potentially send a system message to the user about the error
            await message_service.create_message(
                db,
                session_id=session_id,
                sender_user_id=None,
                sender_type="system",
                message_text="I'm sorry, I encountered an error. Please try again.",
            )
            await db.commit()


@shared_task(name="app.tasks.chat_tasks.generate_session_title_task")
def generate_session_title_task(session_id: str, user_id: str, first_message: str) -> None:
    """
    Background task to generate a meaningful title for a new session.
    """
    asyncio.run(_generate_session_title(UUID(session_id), UUID(user_id), first_message))


async def _generate_session_title(session_id: UUID, user_id: UUID, first_message: str) -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        try:
            new_title = await ai_service.generate_title(first_message)
            if new_title:
                from app.schemas.chat import ChatSessionUpdate
                await session_service.update_session(
                    db,
                    session_id=session_id,
                    user_id=user_id,
                    obj_in=ChatSessionUpdate(session_title=new_title),
                )
                await db.commit()
                logger.info(
                    "session_title_generated_background",
                    chat_session_id=str(session_id),
                    new_title=new_title,
                )
        except Exception as e:
            logger.warning(
                "session_titling_task_failed",
                chat_session_id=str(session_id),
                error=str(e),
            )
