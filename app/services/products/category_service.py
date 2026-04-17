from typing import Any, Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_categories import ProductCategory
from app.repositories.product_categories import product_category_repository
from app.schemas.product_categories import ProductCategoryCreate, ProductCategoryUpdate

class CategoryService:
    async def get_all_categories(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[ProductCategory]:
        return await product_category_repository.get_multi(db, skip=skip, limit=limit)

    async def get_category(self, db: AsyncSession, category_id: Any) -> ProductCategory:
        category = await product_category_repository.get(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    async def create_category(self, db: AsyncSession, *, obj_in: ProductCategoryCreate) -> ProductCategory:
        if await product_category_repository.get_by_name(db, obj_in.category_name):
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        return await product_category_repository.create(db, obj_in=obj_in)

    async def update_category(self, db: AsyncSession, *, category_id: Any, obj_in: ProductCategoryUpdate) -> ProductCategory:
        category = await self.get_category(db, category_id)
        if obj_in.category_name and obj_in.category_name != category.category_name:
            if await product_category_repository.get_by_name(db, obj_in.category_name):
                raise HTTPException(status_code=400, detail="Category with this name already exists")
        return await product_category_repository.update(db, db_obj=category, obj_in=obj_in)

    async def delete_category(self, db: AsyncSession, *, category_id: Any) -> ProductCategory:
        category = await self.get_category(db, category_id)
        return await product_category_repository.delete(db, id=category.product_category_id)

category_service = CategoryService()
