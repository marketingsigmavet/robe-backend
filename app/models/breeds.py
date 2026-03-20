from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Breed(Base):
    __tablename__ = "breeds"
    __table_args__ = (
        UniqueConstraint("species_id", "breed_name", name="uq_breeds_species_id_breed_name"),
    )

    breed_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    species_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pet_species.species_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    breed_name: Mapped[str] = mapped_column(String(100), nullable=False, index=False)
    breed_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    species: Mapped["PetSpecies"] = relationship(back_populates="breeds", lazy="selectin")
    pets: Mapped[list["Pet"]] = relationship(back_populates="breed", lazy="selectin")

