from pydantic import BaseModel, EmailStr, Field

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )
    email: EmailStr
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=PASSWORD_MAX_LENGTH,
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
        max_length=4096,
    )


class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
        max_length=4096,
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class UserRoleUpdate(BaseModel):
    role: str


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserProfileUpdate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=PASSWORD_MAX_LENGTH,
    )
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    profile_image: str | None = None

    model_config = {"from_attributes": True}
