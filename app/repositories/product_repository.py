from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.products import Product
from app.repositories.base import BaseRepository
from app.schemas.products import ProductCreate, ProductUpdate

class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def __init__(self):
        super().__init__(Product)

    async def get_by_sku(self, db: AsyncSession, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku, Product.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().first()

product_repository = ProductRepository()
