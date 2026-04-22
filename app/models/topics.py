from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.chat_sessions import ChatSession
    from app.models.topic_questions import TopicQuestion


class Topic(Base):
    __tablename__ = "topics"

    topic_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    topic_name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

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

    # ── Relationships ──────────────────────────────────────────────────
    questions: Mapped[list["TopicQuestion"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TopicQuestion.sort_order",
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="topic", lazy="selectin"
    )
