from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_brands import ProductBrand
from app.repositories.base import BaseRepository
from app.schemas.product_brands import ProductBrandCreate, ProductBrandUpdate

class ProductBrandRepository(BaseRepository[ProductBrand, ProductBrandCreate, ProductBrandUpdate]):
    def __init__(self):
        super().__init__(ProductBrand)

    async def get_by_name(self, db: AsyncSession, brand_name: str) -> ProductBrand | None:
        stmt = select(ProductBrand).where(
            ProductBrand.brand_name == brand_name,
            ProductBrand.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

product_brand_repository = ProductBrandRepository()
