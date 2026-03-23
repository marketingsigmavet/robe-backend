from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Literal

from app.schemas.users import UserSummary

ChannelType = Literal["email", "mobile"]

class RequestOtpRequest(BaseModel):
    channel: ChannelType
    email: EmailStr | None = None
    mobile_number: str | None = None

    @model_validator(mode="after")
    def check_identifier(self) -> 'RequestOtpRequest':
        if self.channel == "email" and not self.email:
            raise ValueError("email must be provided when channel is 'email'")
        if self.channel == "mobile" and not self.mobile_number:
            raise ValueError("mobile_number must be provided when channel is 'mobile'")
        return self

class RequestOtpResponse(BaseModel):
    message: str
    expires_in_seconds: int
    retry_after_seconds: int | None = None
    destination_hint: str
    dev_otp: str | None = None  # Only populated in debug mode

class VerifyOtpRequest(BaseModel):
    channel: ChannelType
    email: EmailStr | None = None
    mobile_number: str | None = None
    otp_code: str = Field(..., min_length=6, max_length=6)

    @model_validator(mode="after")
    def check_identifier(self) -> 'VerifyOtpRequest':
        if self.channel == "email" and not self.email:
            raise ValueError("email must be provided when channel is 'email'")
        if self.channel == "mobile" and not self.mobile_number:
            raise ValueError("mobile_number must be provided when channel is 'mobile'")
        return self

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool
    onboarding_required: bool
    user: UserSummary

class RefreshTokenRequest(BaseModel):
    refresh_token: str
