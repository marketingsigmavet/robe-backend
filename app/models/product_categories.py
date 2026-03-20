from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.products import Product


class ProductCategory(Base):
    __tablename__ = "product_categories"

    product_category_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    category_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    products: Mapped[list["Product"]] = relationship(back_populates="category", lazy="selectin")

