import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.models.tokens import ActivationTokenModel


class ActivationTokensRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_activation_token(self, user_id: int) -> ActivationTokenModel:
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

    async def get_activation_token(self, token: str) -> ActivationTokenModel | None:
        result = await self.db.execute(select(ActivationTokenModel).filter_by(token=token))
        return result.scalar_one_or_none()

    async def get_activation_token_by_user_id(self, user_id: int) -> ActivationTokenModel | None:
        result = await self.db.execute(select(ActivationTokenModel).filter_by(user_id=user_id))
        return result.scalar_one_or_none()

    async def delete_activation_token(self, token: str) -> None:
        await self.db.execute(delete(ActivationTokenModel).filter_by(token=token))
        await self.db.commit()

    async def delete_expired_token(self) -> None:
        await self.db.execute(
            delete(ActivationTokenModel)
            .where(ActivationTokenModel.expires_at < datetime.now(timezone.utc).replace(tzinfo=None))
        )
        await self.db.commit()
