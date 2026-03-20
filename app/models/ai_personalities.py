from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIPersonality(Base):
    __tablename__ = "ai_personalities"

    personality_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    personality_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    tone_style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="personality", lazy="selectin"
    )

