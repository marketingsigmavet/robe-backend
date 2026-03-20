from typing import Any
from fastapi import APIRouter, Body

router = APIRouter()

@router.get("/me")
async def get_user_settings():
    return {"language": "en", "notifications_enabled": True}

@router.patch("/me")
async def update_user_settings(
    payload: dict[str, Any] = Body(...)
):
    return {"status": "updated"}
