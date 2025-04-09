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


class BaseUserRequest(BaseModel):
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
    def check_password(cls, password: str) -> str:
        validate_password_strength(password)
        return password


class BaseProfileResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    avatar: Optional[str] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None
    user_id: int

    model_config = {
        "from_attributes": True
    }


class BaseUserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }


class UserCreateRequest(BaseUserRequest):
    pass


class UserLoginRequest(BaseUserRequest):
    pass


class UserAdminCreateRequest(BaseUserRequest):
    is_active: Optional[bool] = False
    group: Optional[UserGroupEnum] = UserGroupEnum.USER


class UserCreateResponse(BaseUserResponse):
    created_at: datetime
    message: str


class UserAdminUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    group: Optional[UserGroupEnum] = None


class UserAdminResponse(BaseUserResponse):
    group: UserGroupEnum
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None


class ProfileResponse(BaseProfileResponse):
    pass


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None

    @field_validator("first_name")
    def check_first_name(cls, value: Optional[str]) -> str | None:
        if value is not None:
            return validate_first_name(value)
        return value

    @field_validator("last_name")
    def check_last_name(cls, value: Optional[str]) -> str | None:
        if value is not None:
            return validate_last_name(value)
        return value

    @field_validator("gender")
    def check_gender(cls, value: Optional[GenderEnum]) -> GenderEnum | None:
        if value is not None:
            return validate_gender(value.value)
        return value

    @field_validator("date_of_birth")
    def check_date_of_birth(cls, value: Optional[date]) -> date | None:
        if value is not None:
            return validate_date_of_birth(value)
        return value

    @field_validator("info")
    def check_info(cls, value: Optional[str]) -> str | None:
        if value is not None:
            return validate_info(value)
        return value
