from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.products import Product


class ProductBrand(Base):
    __tablename__ = "product_brands"

    brand_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    brand_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    products: Mapped[list["Product"]] = relationship(back_populates="brand", lazy="selectin")

