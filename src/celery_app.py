from celery import Celery

from src.config.settings import Settings


settings = Settings()

celery_app = Celery(
    "cinema_service",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BROKER_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BACKEND_DB}",
    include=["src.tasks"]
)

celery_app.conf.update(
    result_expires=3600,
    timezone="UTC",
    beat_schedule={
        "delete-expired-tokens-every-hour": {
            "task": "src.tasks.delete_expired_activation_tokens",
            "schedule": 3600.0,
        },
    },
)
