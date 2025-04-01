from celery import Celery

from src.config.logging_settings import logger
from src.config.settings import Settings

settings = Settings()

celery_app = Celery(
    "cinema_service",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BROKER_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BACKEND_DB}",
    include=["src.celery_service.tasks"]
)

logger.info(f"Celery app configured with broker {settings.REDIS_HOST}:{settings.REDIS_PORT} "
            f"and backend {settings.REDIS_HOST}:{settings.REDIS_PORT}.")

celery_app.conf.update(
    result_expires=3600,
    timezone="UTC",
    beat_schedule={
        "delete-expired-tokens-every-hour": {
            "task": "src.celery_service.tasks.delete_expired_activation_tokens",
            "schedule": 3600.0,
        },
        "delete-expired-refresh-tokens-every-3-days": {
            "task": "src.celery_service.tasks.delete_expired_refresh_tokens",
            "schedule": 3 * 24 * 3600.0,
        },
        "delete-expired-password-reset-tokens-every-day": {
            "task": "src.celery_service.tasks.delete_expired_password_reset_tokens",
            "schedule": 24 * 3600.0,
        },
    },
)
logger.info("Celery beat schedule updated with tasks for token expiry management.")

