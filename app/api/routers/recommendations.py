from typing import Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.services.recommendations.recommendation_service import recommendation_service

router = APIRouter()

@router.get("/")
async def list_recommendations(
    db: AsyncSession = Depends(get_db)
):
    user_id = "stub-id"
    return await recommendation_service.get_user_recommendations(db, user_id)

@router.post("/{id}/feedback")
async def submit_feedback(
    id: str,
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve the model
    rec = await recommendation_service.get_recommendation(db, id)
    if rec:
        return await recommendation_service.update_recommendation(db, db_obj=rec, rec_in=payload)
    return {"status": "not_found"}
