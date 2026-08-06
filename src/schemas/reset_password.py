from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(
        min_length=32,
        max_length=255,
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str
    expires_at: str


class ResetPasswordResponse(BaseModel):
    message: str
