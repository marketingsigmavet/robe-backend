from sqlalchemy import Column, ForeignKey, Table
from app.db.base import Base

product_species_link = Table(
    "product_species_link",
    Base.metadata,
    Column("product_id", ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True),
    Column("species_id", ForeignKey("pet_species.species_id", ondelete="CASCADE"), primary_key=True),
)

product_breeds_link = Table(
    "product_breeds_link",
    Base.metadata,
    Column("product_id", ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True),
    Column("breed_id", ForeignKey("breeds.breed_id", ondelete="CASCADE"), primary_key=True),
)
