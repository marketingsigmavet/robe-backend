from app.core.security import create_access_token, create_refresh_token

class TokenService:
    def generate_tokens(self, user_id: str) -> dict[str, str]:
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

token_service = TokenService()
