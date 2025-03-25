from pydantic import BaseModel, EmailStr, field_validator

from src.accounts.validators import validate_password_strength


class JWTTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    def check_password(cls, password: str):
        validate_password_strength(password)
        return password


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    new_password: str

    @field_validator("new_password")
    def check_password_strength(cls, password: str):
        validate_password_strength(password)
        return password
