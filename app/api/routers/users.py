from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user
from app.services.users.user_service import user_service
from app.schemas.users import UserMeResponse, UserUpdateRequest
from app.models.users import User

router = APIRouter()

@router.get("/me", response_model=UserMeResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@router.patch("/me", response_model=UserMeResponse)
async def update_current_user_profile(
    payload: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    updated_user = await user_service.update_me(db, user=current_user, update_data=payload.model_dump(exclude_unset=True))
    return updated_user
