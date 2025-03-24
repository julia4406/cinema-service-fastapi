from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator
from email_validator import validate_email, EmailNotValidError

from src.database.models import GenderEnum, UserGroupEnum
from src.accounts.validators import (
    validate_password_strength,
    validate_info,
    validate_gender,
    validate_last_name,
    validate_first_name,
    validate_date_of_birth,
)


class UserCreateRequest(BaseModel):
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


class UserAdminCreateRequest(BaseModel):
    email: str
    password: str
    is_active: Optional[bool] = False
    group: Optional[UserGroupEnum] = UserGroupEnum.USER


class UserCreateResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    message: str

    model_config = {
        "from_attributes": True
    }


class UserAdminUpdateRequest(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None
    group: Optional[UserGroupEnum] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserAdminResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    group: UserGroupEnum
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    avatar: Optional[str] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None
    user_id: int

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None

    @field_validator("first_name")
    def check_first_name(cls, value: Optional[str]):
        if value is not None:
            return validate_first_name(value)
        return value

    @field_validator("last_name")
    def check_last_name(cls, value: Optional[str]):
        if value is not None:
            return validate_last_name(value)
        return value

    @field_validator("gender")
    def check_gender(cls, value: Optional[GenderEnum]):
        if value is not None:
            return validate_gender(value.value)
        return value

    @field_validator("date_of_birth")
    def check_date_of_birth(cls, value: Optional[date]):
        if value is not None:
            return validate_date_of_birth(value)
        return value

    @field_validator("info")
    def check_info(cls, value: Optional[str]):
        if value is not None:
            return validate_info(value)
        return value
