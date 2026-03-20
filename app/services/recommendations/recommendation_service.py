from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_recommendations import ProductRecommendation
from app.repositories.recommendation_repository import recommendation_repository


class RecommendationService:
    async def create_recommendation(self, db: AsyncSession, *, rec_in: dict[str, Any]) -> ProductRecommendation:
        return await recommendation_repository.create(db, obj_in=rec_in)

    async def get_recommendation(self, db: AsyncSession, rec_id: Any) -> ProductRecommendation | None:
        return await recommendation_repository.get(db, rec_id)

    async def get_user_recommendations(self, db: AsyncSession, user_id: Any) -> Sequence[ProductRecommendation]:
        return await recommendation_repository.get_by_user_id(db, user_id)

    async def update_recommendation(self, db: AsyncSession, *, db_obj: ProductRecommendation, rec_in: dict[str, Any]) -> ProductRecommendation:
        return await recommendation_repository.update(db, db_obj=db_obj, obj_in=rec_in)


recommendation_service = RecommendationService()
