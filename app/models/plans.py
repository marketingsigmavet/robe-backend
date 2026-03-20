from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    plan_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    plan_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    price: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    billing_cycle: Mapped[str | None] = mapped_column(String(50), nullable=True)

    features: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="plan", lazy="selectin"
    )

