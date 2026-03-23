from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.services.auth.otp_service import otp_service
from app.services.auth.token_service import token_service
from app.services.users.user_service import user_service
from app.schemas.auth import AuthTokens


class AuthService:
    async def request_otp(self, redis_client, payload: dict[str, Any]) -> dict:
        channel = payload.get("channel")
        identifier = payload.get("email") if channel == "email" else payload.get("mobile_number")
        if not identifier:
            raise HTTPException(status_code=400, detail="Identifier missing")
            
        return await otp_service.request_otp(redis_client, channel, identifier)

    async def verify_otp_flow(self, db: AsyncSession, redis_client, payload: dict[str, Any]) -> AuthTokens:
        channel = payload.get("channel")
        identifier = payload.get("email") if channel == "email" else payload.get("mobile_number")
        otp_code = payload.get("otp_code")
        
        if not identifier or not otp_code:
            raise HTTPException(status_code=400, detail="Missing identifier or otp_code")

        # 1. Verify OTP
        is_valid = await otp_service.verify_otp(redis_client, channel, identifier, otp_code)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # 2. Get or create user
        is_new_user = False
        if channel == "email":
            user = await user_service.get_user_by_email(db, identifier)
            if not user:
                user = await user_service.create_user(db, user_in={"email": identifier, "is_verified": True})
                is_new_user = True
        else:
            user = await user_service.get_user_by_mobile(db, identifier)
            if not user:
                placeholder_email = f"mobile_{identifier}@placeholder.local"
                user = await user_service.create_user(db, user_in={"email": placeholder_email, "mobile_number": identifier, "is_verified": True})
                is_new_user = True
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="User account is inactive")

        # 3. Generate tokens
        tokens = token_service.generate_tokens(str(user.user_id))
        
        # 4. Check onboarding
        onboarding_required = user_service.is_onboarding_required(user)

        return AuthTokens(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            is_new_user=is_new_user,
            onboarding_required=onboarding_required,
            user=user
        )

    async def refresh_token(self, payload: dict[str, str]) -> dict:
        refresh_token = payload.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token missing")
            
        decoded = verify_token(refresh_token, "refresh")
        if not decoded:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
            
        user_id = decoded.get("sub")
        tokens = token_service.generate_tokens(user_id)
        
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer"
        }

    async def logout(self, redis_client, payload: dict[str, str] | None = None) -> dict:
        return {"status": "success", "message": "Logged out"}


auth_service = AuthService()
