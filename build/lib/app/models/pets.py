from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    species_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pet_species.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    breed_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("breeds.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="pets", lazy="selectin")
    species: Mapped["PetSpecies"] = relationship(back_populates="pets", lazy="selectin")
    breed: Mapped["Breed | None"] = relationship(back_populates="pets", lazy="selectin")

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

