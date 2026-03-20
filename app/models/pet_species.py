from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PetSpecies(Base):
    __tablename__ = "pet_species"

    species_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    species_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    breeds: Mapped[list["Breed"]] = relationship(
        back_populates="species",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pets: Mapped[list["Pet"]] = relationship(
        back_populates="species",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

