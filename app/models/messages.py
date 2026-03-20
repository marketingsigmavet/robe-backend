from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index, UniqueConstraint

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.chat_sessions import ChatSession
    from app.models.chat_attachments import ChatAttachment
    from app.models.product_recommendations import ProductRecommendation
    from app.models.users import User


class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        UniqueConstraint("chat_session_id", "sequence_number", name="uq_messages_chat_session_id_sequence_number"),
        Index("ix_messages_chat_session_id_sequence_number_created_at", "chat_session_id", "sequence_number", "created_at"),
    )

    message_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    chat_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_sessions.chat_session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sender_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)

    message_text: Mapped[str] = mapped_column(Text(), nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)

    message_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    sequence_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    contains_recommendation: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    is_edited: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    chat_session: Mapped["ChatSession"] = relationship(back_populates="messages", lazy="selectin")

    sender_user: Mapped["User | None"] = relationship(
        lazy="selectin",
        foreign_keys=[sender_user_id],
    )

    attachments: Mapped[list["ChatAttachment"]] = relationship(
        back_populates="message", lazy="selectin"
    )
    product_recommendations: Mapped[list["ProductRecommendation"]] = relationship(
        back_populates="message", lazy="selectin"
    )

