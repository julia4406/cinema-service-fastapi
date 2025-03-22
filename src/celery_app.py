from celery import Celery

from src.config.settings import Settings


settings = Settings()

celery_app = Celery(
    "cinema_service",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BROKER_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BACKEND_DB}",
    include=["src.tasks"]
)
