# bot/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    BOT_TOKEN: str
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True
    DB_PATH: str = "storage/db/bot.sqlite3"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()