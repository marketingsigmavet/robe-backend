from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.chat_sessions import ChatSession
    from app.models.messages import Message
    from app.models.pets import Pet
    from app.models.products import Product
    from app.models.recommendation_feedback import RecommendationFeedback


class ProductRecommendation(Base):
    __tablename__ = "product_recommendations"

    __table_args__ = (
        Index(
            "ix_pr_chat_session_product_recommended",
            "chat_session_id",
            "product_id",
            "recommended_at",
        ),
    )

    recommendation_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    chat_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_sessions.chat_session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("messages.message_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pet_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("pets.pet_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    recommendation_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    recommendation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user_clicked: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    user_saved: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    user_purchased: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    recommended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    chat_session: Mapped["ChatSession"] = relationship(back_populates="product_recommendations", lazy="selectin")
    message: Mapped["Message"] = relationship(back_populates="product_recommendations", lazy="selectin")
    product: Mapped["Product"] = relationship(back_populates="product_recommendations", lazy="selectin")
    pet: Mapped["Pet | None"] = relationship(
        back_populates="product_recommendations",
        lazy="selectin",
        foreign_keys=[pet_id],
    )

    feedbacks: Mapped[list["RecommendationFeedback"]] = relationship(
        back_populates="recommendation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

