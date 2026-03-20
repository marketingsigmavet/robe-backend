from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.users import User


class UserPreference(Base):
    __tablename__ = "user_preferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    theme: Mapped[str | None] = mapped_column(String(50), nullable=True)
    app_language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    push_notifications_enabled: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    email_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, default=False
    )
    default_ai_personality: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="preferences", lazy="selectin")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

