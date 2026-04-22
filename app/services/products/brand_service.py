"""Product Brand service."""

from __future__ import annotations

from typing import Any, Sequence

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_brands import ProductBrand
from app.repositories.product_brands import product_brand_repository
from app.schemas.product_brands import ProductBrandCreate, ProductBrandUpdate

logger = structlog.get_logger(__name__)


class BrandService:
    # ── User-facing (active only) ──────────────────────────────────────

    async def get_active_brands(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[ProductBrand]:
        return await product_brand_repository.get_active(
            db, skip=skip, limit=limit, search=search
        )

    async def count_active_brands(
        self, db: AsyncSession, *, search: str | None = None
    ) -> int:
        return await product_brand_repository.count_active(db, search=search)

    async def get_brand_for_user(
        self, db: AsyncSession, brand_id: Any
    ) -> ProductBrand:
        brand = await product_brand_repository.get(db, brand_id)
        if not brand or not brand.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
            )
        return brand

    # ── Admin ──────────────────────────────────────────────────────────

    async def get_all_brands(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ProductBrand]:
        return await product_brand_repository.get_multi(db, skip=skip, limit=limit)

    async def get_brand(self, db: AsyncSession, brand_id: Any) -> ProductBrand:
        brand = await product_brand_repository.get(db, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
            )
        return brand

    async def create_brand(
        self, db: AsyncSession, *, obj_in: ProductBrandCreate
    ) -> ProductBrand:
        if await product_brand_repository.get_by_name(db, obj_in.brand_name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Brand with this name already exists",
            )
        brand = await product_brand_repository.create(db, obj_in=obj_in)
        logger.info(
            "brand_created",
            brand_id=str(brand.brand_id),
            brand_name=brand.brand_name,
        )
        return brand

    async def update_brand(
        self, db: AsyncSession, *, brand_id: Any, obj_in: ProductBrandUpdate
    ) -> ProductBrand:
        brand = await self.get_brand(db, brand_id)
        if obj_in.brand_name and obj_in.brand_name != brand.brand_name:
            if await product_brand_repository.get_by_name(db, obj_in.brand_name):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Brand with this name already exists",
                )
        updated = await product_brand_repository.update(db, db_obj=brand, obj_in=obj_in)
        logger.info(
            "brand_updated",
            brand_id=str(brand.brand_id),
            brand_name=updated.brand_name,
        )
        return updated

    async def delete_brand(
        self, db: AsyncSession, *, brand_id: Any
    ) -> ProductBrand:
        brand = await self.get_brand(db, brand_id)
        deleted = await product_brand_repository.delete(db, id=brand.brand_id)
        logger.info("brand_deleted", brand_id=str(brand.brand_id))
        return deleted


brand_service = BrandService()
