from bot.db.base import Base
from bot.db.db import engine, async_session
from bot.db.seeds import seed_plans


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        await seed_plans(session)