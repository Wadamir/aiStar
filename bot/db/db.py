from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config.settings import settings


def _build_database_url(db_path: str) -> str:
    if "://" in db_path:
        return db_path
    path = Path(db_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite+aiosqlite:///{path.as_posix()}"


DATABASE_URL = _build_database_url(settings.DB_PATH)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)