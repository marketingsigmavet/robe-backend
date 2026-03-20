from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_recommendations import ProductRecommendation
from app.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[ProductRecommendation, Any, Any]):
    def __init__(self):
        super().__init__(ProductRecommendation)

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ProductRecommendation:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> ProductRecommendation | None:
        return await super().get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[ProductRecommendation]:
        return await super().get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: ProductRecommendation, obj_in: dict[str, Any]) -> ProductRecommendation:
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> ProductRecommendation | None:
        return await super().delete(db, id=id)

    async def get_by_user_id(self, db: AsyncSession, user_id: Any) -> Sequence[ProductRecommendation]:
        stmt = select(ProductRecommendation).where(ProductRecommendation.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()


recommendation_repository = RecommendationRepository()
