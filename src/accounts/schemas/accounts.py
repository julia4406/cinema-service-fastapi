from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from email_validator import validate_email, EmailNotValidError
from src.accounts.validators import validate_password_strength


class UserCreateRequestSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    def check_email(cls, email: str) -> str:
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValueError("The email field is not valid")
        return email

    @field_validator("password")
    def check_password(cls, password: str):
        validate_password_strength(password)
        return password


class UserCreateResponseSchema(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    message: str

    model_config = {
        "from_attributes": True
    }


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str
