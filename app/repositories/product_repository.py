"""Product repository."""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product, Any, Any]):
    def __init__(self) -> None:
        super().__init__(Product)

    async def get_by_sku(self, db: AsyncSession, sku: str) -> Product | None:
        stmt = select(Product).where(
            Product.sku == sku,
            Product.is_deleted == False,  # noqa: E712
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        species_id: UUID | None = None,
        search: str | None = None,
    ) -> Sequence[Product]:
        """Active, non-deleted products with optional filters (user-facing)."""
        stmt = select(Product).where(
            Product.is_active == True,  # noqa: E712
            Product.is_deleted == False,  # noqa: E712
        )
        stmt = self._apply_filters(stmt, brand_id=brand_id, category_id=category_id, search=search)
        if species_id:
            stmt = stmt.where(Product.species.any(species_id=species_id))
        stmt = stmt.order_by(Product.product_name).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def count_active(
        self,
        db: AsyncSession,
        *,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        search: str | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(Product)
            .where(
                Product.is_active == True,  # noqa: E712
                Product.is_deleted == False,  # noqa: E712
            )
        )
        stmt = self._apply_filters(stmt, brand_id=brand_id, category_id=category_id, search=search)
        result = await db.execute(stmt)
        return result.scalar_one()

    async def get_all_admin(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> Sequence[Product]:
        """All non-deleted products with admin filters."""
        stmt = select(Product).where(
            Product.is_deleted == False,  # noqa: E712
        )
        stmt = self._apply_filters(stmt, brand_id=brand_id, category_id=category_id, search=search)
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)
        stmt = stmt.order_by(Product.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def count_all_admin(
        self,
        db: AsyncSession,
        *,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(Product)
            .where(Product.is_deleted == False)  # noqa: E712
        )
        stmt = self._apply_filters(stmt, brand_id=brand_id, category_id=category_id, search=search)
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)
        result = await db.execute(stmt)
        return result.scalar_one()

    # ── Internal ────────────────────────────────────────────────────────

    @staticmethod
    def _apply_filters(stmt, *, brand_id=None, category_id=None, search=None):
        if brand_id:
            stmt = stmt.where(Product.brand_id == brand_id)
        if category_id:
            stmt = stmt.where(Product.product_category_id == category_id)
        if search:
            stmt = stmt.where(Product.product_name.ilike(f"%{search}%"))
        return stmt


product_repository = ProductRepository()
