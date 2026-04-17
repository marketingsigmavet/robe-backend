from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product_brands import ProductBrand
    from app.models.product_categories import ProductCategory
    from app.models.product_recommendations import ProductRecommendation
    from app.models.pet_species import PetSpecies
    from app.models.breeds import Breed

from app.models.product_tags import product_species_link, product_breeds_link


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        Index(
            "ix_products_brand_id_category_id_is_active",
            "brand_id",
            "product_category_id",
            "is_active",
        ),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    brand_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_brands.brand_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_categories.product_category_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    life_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)

    usage_guidelines: Mapped[str | None] = mapped_column(Text(), nullable=True)
    ingredients: Mapped[str | None] = mapped_column(Text(), nullable=True)
    benefits: Mapped[str | None] = mapped_column(Text(), nullable=True)

    product_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

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

    brand: Mapped["ProductBrand"] = relationship(back_populates="products", lazy="selectin")
    category: Mapped["ProductCategory"] = relationship(back_populates="products", lazy="selectin")
    
    species: Mapped[list["PetSpecies"]] = relationship(
        secondary=product_species_link,
        lazy="selectin",
    )
    breeds: Mapped[list["Breed"]] = relationship(
        secondary=product_breeds_link,
        lazy="selectin",
    )
    
    product_recommendations: Mapped[list["ProductRecommendation"]] = relationship(
        back_populates="product",
        lazy="selectin",
    )

