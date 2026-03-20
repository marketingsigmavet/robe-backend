from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.chat_sessions import ChatSession
    from app.models.breeds import Breed
    from app.models.pet_species import PetSpecies
    from app.models.product_recommendations import ProductRecommendation
    from app.models.users import User


class Pet(Base):
    __tablename__ = "pets"

    pet_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    species_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pet_species.species_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    breed_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("breeds.breed_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    pet_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date(), nullable=True)
    age_in_months: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    weight_kg: Mapped[sa.Numeric | None] = mapped_column(Numeric(6, 2), nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_neutered: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)

    medical_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    allergies: Mapped[dict | list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    dietary_preferences: Mapped[dict | list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    activity_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

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

    owner: Mapped["User"] = relationship(back_populates="pets", lazy="selectin")
    species: Mapped["PetSpecies"] = relationship(back_populates="pets", lazy="selectin")
    breed: Mapped["Breed | None"] = relationship(back_populates="pets", lazy="selectin")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="pet",
        lazy="selectin",
    )
    product_recommendations: Mapped[list["ProductRecommendation"]] = relationship(
        back_populates="pet",
        lazy="selectin",
    )

