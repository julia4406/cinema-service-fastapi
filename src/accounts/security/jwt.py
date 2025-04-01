import jwt
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings
from src.database.models import UserModel, RefreshTokenModel
from src.accounts.repositories.accounts import UserRepository
from src.accounts.repositories.tokens import RefreshTokensRepository
from src.accounts.security.jwt_config import (
    private_key,
    public_key,
    JWT_ALGORITHM,
    ACCESS_EXPIRE_MINUTES,
    REFRESH_EXPIRE_DAYS
)


settings = Settings()


class JWTAuthManager:
    def __init__(self):
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = JWT_ALGORITHM
        self.access_expire_minutes = ACCESS_EXPIRE_MINUTES
        self.refresh_expire_days = REFRESH_EXPIRE_DAYS

    def create_access_token(self, user: UserModel):
        payload = {
            "sub": user.email,
            "type": "access",
            "group": user.group_id,
            "exp": datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=self.access_expire_minutes)
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    async def create_refresh_token(self, user: UserModel, db: AsyncSession):

        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=self.refresh_expire_days)

        payload = {
            "sub": user.email,
            "type": "refresh",
            "group": user.group_id,
            "exp": expires_at
        }

        token = jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        db_token = RefreshTokenModel(
            token=token,
            user_id=user.id,
            expires_at=expires_at
        )

        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)

        return token

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token is expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    async def verify_access_token(self, token: str, db: AsyncSession):
        payload = self.decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("Token is not valid")
        email = payload.get("sub")
        user = await UserRepository(db).get_by_email(email=email)
        if not user:
            raise ValueError("User not found")
        return user

    async def verify_refresh_token(self, token: str, db: AsyncSession):
        payload = self.decode_token(token)
        if payload.get("type") != "refresh":
            raise ValueError("Token is not valid")
        email = payload.get("sub")
        user = await UserRepository(db).get_by_email(email=email)
        if not user:
            raise ValueError("User not found")

        refresh_token = await RefreshTokensRepository(db).get_refresh_token(user_id=user.id, token=token)
        if not refresh_token or refresh_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            raise ValueError("Refresh token is not valid")
        return user


def get_jwt_service():
    return JWTAuthManager()
