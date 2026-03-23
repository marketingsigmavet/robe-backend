import random
from fastapi import HTTPException, status
from app.core.config import get_settings
from app.cache.keys import get_otp_challenge_key, get_otp_attempts_key, get_otp_cooldown_key

class OtpService:
    def generate_otp(self) -> str:
        return f"{random.randint(0, 999999):06d}"

    async def request_otp(self, redis_client, channel: str, identifier: str) -> dict:
        settings = get_settings()
        cooldown_key = get_otp_cooldown_key(channel, identifier)
        is_cooldown = await redis_client.get(cooldown_key)
        if is_cooldown:
            ttl = await redis_client.ttl(cooldown_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {ttl} seconds before requesting a new OTP"
            )

        otp_code = self.generate_otp()
        
        challenge_key = get_otp_challenge_key(channel, identifier)
        attempts_key = get_otp_attempts_key(channel, identifier)
        
        await redis_client.setex(challenge_key, settings.otp_expire_seconds, otp_code)
        await redis_client.setex(attempts_key, settings.otp_expire_seconds, 0)
        await redis_client.setex(cooldown_key, settings.otp_resend_cooldown_seconds, "1")

        print(f"[{channel.upper()}] Sent OTP {otp_code} to {identifier}")

        masked_identifier = self._mask_identifier(channel, identifier)
        response = {
            "message": "OTP sent successfully",
            "expires_in_seconds": settings.otp_expire_seconds,
            "destination_hint": masked_identifier,
        }
        
        if settings.debug_mode:
            response["dev_otp"] = otp_code

        return response

    async def verify_otp(self, redis_client, channel: str, identifier: str, otp_code: str) -> bool:
        settings = get_settings()
        challenge_key = get_otp_challenge_key(channel, identifier)
        attempts_key = get_otp_attempts_key(channel, identifier)
        
        stored_otp = await redis_client.get(challenge_key)
        if not stored_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired or invalid"
            )

        attempts = await redis_client.incr(attempts_key)
        if attempts > settings.otp_max_attempts:
            await redis_client.delete(challenge_key)
            await redis_client.delete(attempts_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many invalid OTP attempts. Please request a new one."
            )

        if str(stored_otp) != str(otp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code"
            )

        await redis_client.delete(challenge_key)
        await redis_client.delete(attempts_key)
        return True

    def _mask_identifier(self, channel: str, identifier: str) -> str:
        if channel == "email":
            parts = identifier.split('@')
            if len(parts) == 2:
                name, domain = parts
                if len(name) > 2:
                    return f"{name[:2]}***@{domain}"
                return f"*@{domain}"
        elif channel == "mobile":
            if len(identifier) > 4:
                return f"***-***-{identifier[-4:]}"
        return "***"

otp_service = OtpService()
