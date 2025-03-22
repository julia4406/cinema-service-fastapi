from celery import shared_task
from sqlalchemy import delete
from src.database.session_postgresql import get_postgresql_db
from src.database.models.tokens import ActivationTokenModel
from datetime import datetime, timezone

@shared_task
def delete_expired_activation_tokens():
    async def async_task():
        async for db in get_postgresql_db():
            stmt = delete(ActivationTokenModel).where(
                ActivationTokenModel.expires_at < datetime.now(timezone.utc).replace(tzinfo=None)
            )
            await db.execute(stmt)
            await db.commit()

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_task())
