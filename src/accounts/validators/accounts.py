import re
from datetime import date

from src.database.models import GenderEnum


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lower letter.")
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r'[@$!%*?&#]', password):
        raise ValueError("Password must contain at least one special character: @, $, !, %, *, ?, #, &.")


def validate_first_name(value: str) -> str:
    if not value.isalpha():
        raise ValueError("First name must contain only letters")
    if len(value) < 2:
        raise ValueError("First name must be at least 2 characters long")
    return value


def validate_last_name(value: str) -> str:
    if not value.isalpha():
        raise ValueError("Last name must contain only letters")
    if len(value) < 2:
        raise ValueError("Last name must be at least 2 characters long")
    return value


def validate_gender(value: GenderEnum) -> GenderEnum:
    allowed_genders = ["man", "woman"]
    if value not in allowed_genders:
        raise ValueError("Invalid gender value")
    return value


def validate_date_of_birth(value: date) -> date:
    today = date.today()
    if value > today:
        raise ValueError("Date of birth cannot be in the future")
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 13:
        raise ValueError("User must be at least 13 years old")
    if age > 120:
        raise ValueError("User must be at most 120 years old")
    return value


def validate_info(value: str) -> str:
    if len(value) > 200:
        raise ValueError("Info cannot exceed 200 characters")
    return value
