import jwt
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from src.config.settings import Settings
from src.database.models import UserModel

settings = Settings()


class JWTAuthManager:
    def __init__(self):
        with open(settings.PRIVATE_KEY_PATH, "rb") as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        with open(settings.PUBLIC_KEY_PATH, "rb") as key_file:
            self.public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        self.algorithm = settings.JWT_ALGORITHM
        self.access_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    async def create_access_token(self, user: UserModel):
        payload = {
            "sub": user.email,
            "type": "access",
            "group": user.group_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_expire_minutes)
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    async def create_refresh_token(self, user: UserModel):
        payload = {
            "sub": user.email,
            "type": "refresh",
            "group": user.group_id,
            "exp": datetime.now(timezone.utc) + timedelta(days=self.refresh_expire_days)
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
