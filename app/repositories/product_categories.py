from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_categories import ProductCategory
from app.repositories.base import BaseRepository
from app.schemas.product_categories import ProductCategoryCreate, ProductCategoryUpdate

class ProductCategoryRepository(BaseRepository[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    def __init__(self):
        super().__init__(ProductCategory)

    async def get_by_name(self, db: AsyncSession, category_name: str) -> ProductCategory | None:
        stmt = select(ProductCategory).where(
            ProductCategory.category_name == category_name,
            ProductCategory.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

product_category_repository = ProductCategoryRepository()
