"""Product Brand repository."""

from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_brands import ProductBrand
from app.repositories.base import BaseRepository


class ProductBrandRepository(BaseRepository[ProductBrand, Any, Any]):
    def __init__(self) -> None:
        super().__init__(ProductBrand)

    async def get_by_name(
        self, db: AsyncSession, brand_name: str
    ) -> ProductBrand | None:
        stmt = select(ProductBrand).where(
            ProductBrand.brand_name == brand_name,
            ProductBrand.is_deleted == False,  # noqa: E712
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[ProductBrand]:
        """Return only active, non-deleted brands (for user-facing endpoints)."""
        stmt = select(ProductBrand).where(
            ProductBrand.is_active == True,  # noqa: E712
            ProductBrand.is_deleted == False,  # noqa: E712
        )
        if search:
            stmt = stmt.where(ProductBrand.brand_name.ilike(f"%{search}%"))
        stmt = stmt.order_by(ProductBrand.brand_name).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_active(
        self, db: AsyncSession, *, search: str | None = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(ProductBrand)
            .where(
                ProductBrand.is_active == True,  # noqa: E712
                ProductBrand.is_deleted == False,  # noqa: E712
            )
        )
        if search:
            stmt = stmt.where(ProductBrand.brand_name.ilike(f"%{search}%"))
        result = await db.execute(stmt)
        return result.scalar_one()


product_brand_repository = ProductBrandRepository()
