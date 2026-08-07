from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(
        min_length=32,
        max_length=255,
    )
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str
    expires_at: str


class ResetPasswordResponse(BaseModel):
    message: str
