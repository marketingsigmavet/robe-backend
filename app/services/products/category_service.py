"""Product Category service."""

from __future__ import annotations

from typing import Any, Sequence

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_categories import ProductCategory
from app.repositories.product_categories import product_category_repository
from app.schemas.product_categories import ProductCategoryCreate, ProductCategoryUpdate

logger = structlog.get_logger(__name__)


class CategoryService:
    # ── User-facing (active only) ──────────────────────────────────────

    async def get_active_categories(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[ProductCategory]:
        return await product_category_repository.get_active(
            db, skip=skip, limit=limit, search=search
        )

    async def count_active_categories(
        self, db: AsyncSession, *, search: str | None = None
    ) -> int:
        return await product_category_repository.count_active(db, search=search)

    async def get_category_for_user(
        self, db: AsyncSession, category_id: Any
    ) -> ProductCategory:
        category = await product_category_repository.get(db, category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return category

    # ── Admin ──────────────────────────────────────────────────────────

    async def get_all_categories(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ProductCategory]:
        return await product_category_repository.get_multi(db, skip=skip, limit=limit)

    async def get_category(
        self, db: AsyncSession, category_id: Any
    ) -> ProductCategory:
        category = await product_category_repository.get(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return category

    async def create_category(
        self, db: AsyncSession, *, obj_in: ProductCategoryCreate
    ) -> ProductCategory:
        if await product_category_repository.get_by_name(db, obj_in.category_name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )
        category = await product_category_repository.create(db, obj_in=obj_in)
        logger.info(
            "category_created",
            category_id=str(category.product_category_id),
            category_name=category.category_name,
        )
        return category

    async def update_category(
        self,
        db: AsyncSession,
        *,
        category_id: Any,
        obj_in: ProductCategoryUpdate,
    ) -> ProductCategory:
        category = await self.get_category(db, category_id)
        if obj_in.category_name and obj_in.category_name != category.category_name:
            if await product_category_repository.get_by_name(db, obj_in.category_name):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category with this name already exists",
                )
        updated = await product_category_repository.update(
            db, db_obj=category, obj_in=obj_in
        )
        logger.info(
            "category_updated",
            category_id=str(category.product_category_id),
            category_name=updated.category_name,
        )
        return updated

    async def delete_category(
        self, db: AsyncSession, *, category_id: Any
    ) -> ProductCategory:
        category = await self.get_category(db, category_id)
        deleted = await product_category_repository.delete(
            db, id=category.product_category_id
        )
        logger.info(
            "category_deleted",
            category_id=str(category.product_category_id),
        )
        return deleted


category_service = CategoryService()
