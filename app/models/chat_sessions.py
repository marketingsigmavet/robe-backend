from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ai_personalities import AIPersonality
    from app.models.pets import Pet
    from app.models.topics import Topic
    from app.models.messages import Message
    from app.models.chat_attachments import ChatAttachment
    from app.models.saved_chats import SavedChat
    from app.models.product_recommendations import ProductRecommendation
    from app.models.users import User


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    __table_args__ = (
        Index(
            "ix_chat_sessions_user_id_started_at_last_message_at",
            "user_id",
            "started_at",
            "last_message_at",
        ),
    )

    chat_session_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pet_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("pets.pet_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("topics.topic_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    personality_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ai_personalities.personality_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    session_title: Mapped[str] = mapped_column(String(200), nullable=False)
    session_type: Mapped[str] = mapped_column(String(50), nullable=False)
    session_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)

    is_general_chat: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="chat_sessions", lazy="selectin")
    pet: Mapped["Pet | None"] = relationship(back_populates="chat_sessions", lazy="selectin")
    topic: Mapped["Topic | None"] = relationship(back_populates="chat_sessions", lazy="selectin")
    personality: Mapped["AIPersonality | None"] = relationship(
        back_populates="chat_sessions", lazy="selectin"
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat_session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attachments: Mapped[list["ChatAttachment"]] = relationship(
        back_populates="chat_session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    saved_chats: Mapped[list["SavedChat"]] = relationship(
        back_populates="chat_session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    product_recommendations: Mapped[list["ProductRecommendation"]] = relationship(
        back_populates="chat_session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

