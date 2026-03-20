from typing import Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db

router = APIRouter()

@router.post("/request-otp")
async def request_otp(
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    return {"status": "otp_sent"}

@router.post("/verify-otp")
async def verify_otp(
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    return {"token": "sample-jwt-token"}

@router.post("/refresh")
async def refresh_token(
    db: AsyncSession = Depends(get_db)
):
    return {"token": "new-jwt-token"}

@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db)
):
    return {"status": "logged_out"}
