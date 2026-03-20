from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SavedChat(Base):
    __tablename__ = "saved_chats"

    __table_args__ = (
        UniqueConstraint("user_id", "chat_session_id", name="uq_saved_chats_user_id_chat_session_id"),
    )

    saved_chat_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chat_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_sessions.chat_session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="saved_chats", lazy="selectin")
    chat_session: Mapped["ChatSession"] = relationship(back_populates="saved_chats", lazy="selectin")

