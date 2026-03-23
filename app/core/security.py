from datetime import datetime, timedelta, timezone
from typing import Any
import jwt

from app.core.config import get_settings


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> dict[str, Any] | None:
    settings = get_settings()
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if decoded_token.get("type") != expected_type:
            return None
        return decoded_token
    except jwt.PyJWTError:
        return None
