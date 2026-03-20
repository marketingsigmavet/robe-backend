from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product_recommendations import ProductRecommendation
    from app.models.users import User


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    feedback_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_recommendations.recommendation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    feedback_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    was_helpful: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    recommendation: Mapped["ProductRecommendation"] = relationship(
        back_populates="feedbacks", lazy="selectin"
    )
    user: Mapped["User"] = relationship(back_populates="recommendation_feedback", lazy="selectin")

