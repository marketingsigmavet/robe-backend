from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.api.deps.db import get_db
from app.cache.redis import get_redis
from app.services.auth.auth_service import auth_service
from app.schemas.auth import (
    RequestOtpRequest,
    RequestOtpResponse,
    VerifyOtpRequest,
    AuthTokens,
    RefreshTokenRequest
)

router = APIRouter()

@router.post("/request-otp", response_model=RequestOtpResponse)
async def request_otp(
    payload: RequestOtpRequest,
    redis_client = Depends(get_redis)
):
    return await auth_service.request_otp(redis_client, payload.model_dump())

@router.post("/verify-otp", response_model=AuthTokens)
async def verify_otp(
    payload: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db),
    redis_client = Depends(get_redis)
):
    return await auth_service.verify_otp_flow(db, redis_client, payload.model_dump())

@router.post("/refresh")
async def refresh_token(
    payload: RefreshTokenRequest
):
    return await auth_service.refresh_token(payload.model_dump())

@router.post("/logout")
async def logout(
    redis_client = Depends(get_redis)
):
    return await auth_service.logout(redis_client)
