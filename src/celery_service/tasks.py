from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy import delete

from src.config.logging_settings import logger
from src.database.models import PasswordResetTokenModel, RefreshTokenModel
from src.database.models.tokens import ActivationTokenModel
from src.database.session_postgresql import get_postgresql_db


@shared_task
def delete_expired_activation_tokens():
    async def async_task():
        async for db in get_postgresql_db():
            stmt = delete(ActivationTokenModel).where(
                ActivationTokenModel.expires_at < datetime.now(timezone.utc).replace(tzinfo=None)
            )
            await db.execute(stmt)
            await db.commit()
        logger.info("Expired activation tokens deleted.")

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())


@shared_task
def delete_expired_refresh_tokens():
    async def async_task():
        async for db in get_postgresql_db():
            stmt = delete(RefreshTokenModel).where(
                RefreshTokenModel.expires_at < datetime.now(timezone.utc).replace(tzinfo=None)
            )
            await db.execute(stmt)
            await db.commit()
        logger.info("Expired refresh tokens deleted.")

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())


@shared_task
def delete_expired_password_reset_tokens():
    async def async_task():
        async for db in get_postgresql_db():
            stmt = delete(PasswordResetTokenModel).where(
                PasswordResetTokenModel.expires_at < datetime.now(timezone.utc).replace(tzinfo=None)
            )
            await db.execute(stmt)
            await db.commit()
        logger.info("Expired password reset tokens deleted.")

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())
