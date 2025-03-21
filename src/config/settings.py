from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1/"

    # Формуємо шлях до бази даних, коректно обробляючи шляхи для SQLite
    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'db.sqlite3'}"

    db_echo: bool = True


settings = Settings()

