"""
TopicQuestion model and its M2M link tables for species, breeds, and products.

A question belongs to a topic and can be tagged with species, breeds, and
products so the frontend can filter / suggest questions relevant to the
user's pet and product context.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.breeds import Breed
    from app.models.pet_species import PetSpecies
    from app.models.products import Product
    from app.models.topics import Topic


# ---------------------------------------------------------------------------
# M2M link tables
# ---------------------------------------------------------------------------

question_species_link = Table(
    "question_species_link",
    Base.metadata,
    Column(
        "question_id",
        ForeignKey("topic_questions.question_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "species_id",
        ForeignKey("pet_species.species_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

question_breeds_link = Table(
    "question_breeds_link",
    Base.metadata,
    Column(
        "question_id",
        ForeignKey("topic_questions.question_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "breed_id",
        ForeignKey("breeds.breed_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

question_products_link = Table(
    "question_products_link",
    Base.metadata,
    Column(
        "question_id",
        ForeignKey("topic_questions.question_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "product_id",
        ForeignKey("products.product_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# ---------------------------------------------------------------------------
# TopicQuestion model
# ---------------------------------------------------------------------------

class TopicQuestion(Base):
    __tablename__ = "topic_questions"

    question_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.topic_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_text: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
    topic: Mapped["Topic"] = relationship(back_populates="questions", lazy="selectin")

    species: Mapped[list["PetSpecies"]] = relationship(
        secondary=question_species_link, lazy="selectin"
    )
    breeds: Mapped[list["Breed"]] = relationship(
        secondary=question_breeds_link, lazy="selectin"
    )
    products: Mapped[list["Product"]] = relationship(
        secondary=question_products_link, lazy="selectin"
    )
