import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.models.tokens import ActivationTokenModel, RefreshTokenModel, PasswordResetTokenModel
from src.config.logging_settings import logger


class ActivationTokensRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_activation_token(self, user_id: int) -> ActivationTokenModel:
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            expires_at_naive = expires_at.replace(tzinfo=None)

            activation_token = ActivationTokenModel(
                token=token,
                expires_at=expires_at_naive,
                user_id=user_id
            )
            self.db.add(activation_token)
            await self.db.commit()
            await self.db.refresh(activation_token)
            return activation_token
        except Exception as e:
            logger.error(f"Error creating activation token for user {user_id}: {e}")
            raise

    async def get_activation_token(self, token: str) -> ActivationTokenModel | None:
        try:
            result = await self.db.execute(select(ActivationTokenModel).filter_by(token=token))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching activation token {token}: {e}")
            raise

    async def get_activation_token_by_user_id(self, user_id: int) -> ActivationTokenModel | None:
        try:
            result = await self.db.execute(select(ActivationTokenModel).filter_by(user_id=user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching activation token for user {user_id}: {e}")
            raise

    async def delete_activation_token(self, token: str) -> None:
        try:
            await self.db.execute(delete(ActivationTokenModel).filter_by(token=token))
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting activation token {token}: {e}")
            raise

    async def delete_expired_token(self) -> None:
        try:
            await self.db.execute(
                delete(ActivationTokenModel)
                .where(ActivationTokenModel.expires_at < datetime.now(timezone.utc).replace(tzinfo=None))
            )
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting expired activation tokens: {e}")
            raise


class RefreshTokensRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_refresh_token(self, token: str, user_id: int) -> RefreshTokenModel | None:
        try:
            result = await self.db.execute(select(RefreshTokenModel).filter_by(user_id=user_id, token=token))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching refresh token {token} for user {user_id}: {e}")
            raise

    async def delete_all_by_user_id(self, user_id: int) -> RefreshTokenModel | None:
        try:
            await self.db.execute(delete(RefreshTokenModel).filter_by(user_id=user_id))
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting all refresh tokens for user {user_id}: {e}")
            raise


class PasswordResetTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reset_token(self, user_id: int) -> PasswordResetTokenModel:
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
            reset_token = PasswordResetTokenModel(
                token=token,
                expires_at=expires_at,
                user_id=user_id
            )
            self.db.add(reset_token)
            await self.db.commit()
            await self.db.refresh(reset_token)
            return reset_token
        except Exception as e:
            logger.error(f"Error creating reset token for user {user_id}: {e}")
            raise

    async def get_reset_token_by_user_id(self, user_id: int) -> PasswordResetTokenModel | None:
        try:
            result = await self.db.execute(select(PasswordResetTokenModel).filter_by(user_id=user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching reset token for user {user_id}: {e}")
            raise

    async def get_reset_token(self, token: str) -> PasswordResetTokenModel | None:
        try:
            result = await self.db.execute(select(PasswordResetTokenModel).filter_by(token=token))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching reset token {token}: {e}")
            raise

    async def delete_reset_token(self, token: str) -> None:
        try:
            await self.db.execute(delete(PasswordResetTokenModel).filter_by(token=token))
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting reset token {token}: {e}")
            raise

    async def verify_reset_token(self, token: str) -> PasswordResetTokenModel:
        try:
            reset_token = await self.get_reset_token(token)
            if not reset_token or reset_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
                raise ValueError("Token is invalid")
            return reset_token
        except Exception as e:
            logger.error(f"Error verifying reset token {token}: {e}")
            raise
