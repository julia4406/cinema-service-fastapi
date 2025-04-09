from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class AppPathsSettings(BaseSettings):
    ROOT_DIR: Path = Path(__file__).parent.parent.parent
    BASE_DIR: Path = Path(__file__).parent.parent
    PATH_TO_DB: str = str(BASE_DIR / "database" / "source" / "theater.db")
    PATH_TO_MOVIES_CSV: str = str(BASE_DIR / "database" / "seed_data" / "imdb_movies.csv")


class JWTSettings(BaseSettings):
    PRIVATE_KEY_PATH: Path = Path(__file__).parent.parent.parent / "private_key.pem"
    PUBLIC_KEY_PATH: Path = Path(__file__).parent.parent.parent / "public_key.pem"
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
    )


class PostgresSettings(BaseSettings):
    USER: str = "test_user"
    PASSWORD: str = "test_password"
    HOST: str = "test_host"
    DB_PORT: int = 5432
    DB: str = "test_db"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="POSTGRES_",
    )


class RedisSettings(BaseSettings):
    HOST: str
    PORT: int
    BROKER_DB: int
    BACKEND_DB: int

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="REDIS_",
    )


class MailSettings(BaseSettings):
    USERNAME: str
    PASSWORD: str
    FROM: str
    FROM_NAME: str
    PORT: int = 587
    SERVER: str
    STARTTLS: bool = True
    SSL_TLS: bool = True

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="MAIL_",
    )


class AWSSettings(BaseSettings):
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    S3_BUCKET: str
    AWS_REGION: Optional[str] = "us-east-1"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
    )


class StripeSettings(BaseSettings):
    SECRET_KEY: str
    WEBHOOK_SECRET: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="STRIPE_",
    )


class ServiceSettings(BaseSettings):
    SERVICE_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
    )


class BaseAppSettings(AppPathsSettings, JWTSettings):
    LOGIN_TIME_DAYS: int = 7


class Settings(
    BaseAppSettings, PostgresSettings, RedisSettings, MailSettings, AWSSettings, StripeSettings, ServiceSettings
):
    pass
