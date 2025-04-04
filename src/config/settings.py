import os
from pathlib import Path
from typing import Any, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class AppPathsSettings(BaseSettings):
    ROOT_DIR: Path = Path(__file__).parent.parent.parent
    BASE_DIR: Path = Path(__file__).parent.parent
    PATH_TO_DB: str = str(BASE_DIR / "database" / "source" / "theater.db")
    PATH_TO_MOVIES_CSV: str = str(BASE_DIR / "database" / "seed_data" / "imdb_movies.csv")


class JWTSettings(BaseSettings):
    PRIVATE_KEY_PATH: Path = os.getenv("PRIVATE_KEY_PATH", (Path(__file__).parent.parent.parent / "private_key.pem"))
    PUBLIC_KEY_PATH: Path = os.getenv("PUBLIC_KEY_PATH", (Path(__file__).parent.parent.parent / "public_key.pem"))
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class PostgresSettings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "test_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "test_password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "test_host")
    POSTGRES_DB_PORT: int = int(os.getenv("POSTGRES_DB_PORT", 5432))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "test_db")


class RedisSettings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")
    REDIS_BROKER_DB: int = os.getenv("REDIS_BROKER_DB")
    REDIS_BACKEND_DB: int = os.getenv("REDIS_BACKEND_DB")


class MailSettings(BaseSettings):
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True") == "True"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False") == "True"


class AWSSettings(BaseSettings):
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_KEY")
    S3_BUCKET: str = os.getenv("S3_BUCKET")
    AWS_REGION: Optional[str] = os.getenv("AWS_REGION", "us-east-1")


class StripeSettings(BaseSettings):
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET")


class ServiceSettings(BaseSettings):
    SERVICE_URL: str = os.getenv("SERVICE_URL")


class BaseAppSettings(AppPathsSettings, JWTSettings):
    LOGIN_TIME_DAYS: int = 7


class Settings(
    BaseAppSettings, PostgresSettings, RedisSettings, MailSettings, AWSSettings, StripeSettings, ServiceSettings
):
    pass


class TestingSettings(BaseAppSettings):
    SECRET_KEY_ACCESS: str = "SECRET_KEY_ACCESS"
    SECRET_KEY_REFRESH: str = "SECRET_KEY_REFRESH"
    JWT_SIGNING_ALGORITHM: str = "HS256"

    def model_post_init(self, __context: dict[str, Any] | None = None) -> None:
        object.__setattr__(self, 'PATH_TO_DB', ":memory:")
        object.__setattr__(
            self,
            'PATH_TO_MOVIES_CSV',
            str(self.BASE_DIR / "database" / "seed_data" / "test_data.csv")
        )
