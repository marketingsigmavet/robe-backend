from typing import Any, Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_brands import ProductBrand
from app.repositories.product_brands import product_brand_repository
from app.schemas.product_brands import ProductBrandCreate, ProductBrandUpdate

class BrandService:
    async def get_all_brands(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[ProductBrand]:
        return await product_brand_repository.get_multi(db, skip=skip, limit=limit)

    async def get_brand(self, db: AsyncSession, brand_id: Any) -> ProductBrand:
        brand = await product_brand_repository.get(db, brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        return brand

    async def create_brand(self, db: AsyncSession, *, obj_in: ProductBrandCreate) -> ProductBrand:
        if await product_brand_repository.get_by_name(db, obj_in.brand_name):
            raise HTTPException(status_code=400, detail="Brand with this name already exists")
        return await product_brand_repository.create(db, obj_in=obj_in)

    async def update_brand(self, db: AsyncSession, *, brand_id: Any, obj_in: ProductBrandUpdate) -> ProductBrand:
        brand = await self.get_brand(db, brand_id)
        if obj_in.brand_name and obj_in.brand_name != brand.brand_name:
            if await product_brand_repository.get_by_name(db, obj_in.brand_name):
                raise HTTPException(status_code=400, detail="Brand with this name already exists")
        return await product_brand_repository.update(db, db_obj=brand, obj_in=obj_in)

    async def delete_brand(self, db: AsyncSession, *, brand_id: Any) -> ProductBrand:
        brand = await self.get_brand(db, brand_id)
        return await product_brand_repository.delete(db, id=brand.brand_id)

brand_service = BrandService()
