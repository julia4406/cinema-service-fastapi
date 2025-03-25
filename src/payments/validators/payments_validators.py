from pydantic import EmailStr, ValidationError


def validate_email(email: str) -> EmailStr:
    try:
        validated_email = EmailStr(email)
        return validated_email
    except ValidationError:
        raise ValueError(f"Invalid email format: {email}")