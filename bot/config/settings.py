# bot/config/settings.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int] = []
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True

    # Paths
    DB_PATH: str = "storage/db/bot.sqlite3"
    STORAGE_PATH: str = "storage/voices"
    BEATS_PATH: str = "storage/beats"
    PROCESSED_PATH: str = "storage/processed"

    # AI
    AUPHONIC_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()