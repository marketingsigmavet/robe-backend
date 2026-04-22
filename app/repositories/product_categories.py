"""Product Category repository."""

from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_categories import ProductCategory
from app.repositories.base import BaseRepository


class ProductCategoryRepository(BaseRepository[ProductCategory, Any, Any]):
    def __init__(self) -> None:
        super().__init__(ProductCategory)

    async def get_by_name(
        self, db: AsyncSession, category_name: str
    ) -> ProductCategory | None:
        stmt = select(ProductCategory).where(
            ProductCategory.category_name == category_name,
            ProductCategory.is_deleted == False,  # noqa: E712
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
    ) -> Sequence[ProductCategory]:
        """Return only active, non-deleted categories (for user-facing endpoints)."""
        stmt = select(ProductCategory).where(
            ProductCategory.is_active == True,  # noqa: E712
            ProductCategory.is_deleted == False,  # noqa: E712
        )
        if search:
            stmt = stmt.where(ProductCategory.category_name.ilike(f"%{search}%"))
        stmt = stmt.order_by(ProductCategory.category_name).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_active(
        self, db: AsyncSession, *, search: str | None = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(ProductCategory)
            .where(
                ProductCategory.is_active == True,  # noqa: E712
                ProductCategory.is_deleted == False,  # noqa: E712
            )
        )
        if search:
            stmt = stmt.where(ProductCategory.category_name.ilike(f"%{search}%"))
        result = await db.execute(stmt)
        return result.scalar_one()


product_category_repository = ProductCategoryRepository()
