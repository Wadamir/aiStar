from loguru import logger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.plan import Plan


async def seed_plans(session: AsyncSession) -> None:
    result = await session.execute(select(Plan))
    existing = result.scalars().all()
    
    if existing:
        logger.info("Plans already seeded")
        return
    
    logger.info("Seeding plans")
    plans = [
        Plan(
            id=0,
            name="free",
            daily_limit=2,
            priority=0,
            description="Free plan",
            price_stars=0,
            is_active=True,
        ),
        Plan(
            id=1,
            name="pro",
            daily_limit=20,
            priority=1,
            description="Pro plan",
            price_stars=199,
            is_active=True,
        ),
        Plan(
            id=2,
            name="star",
            daily_limit=100,
            priority=2,
            description="Star plan",
            price_stars=499,
            is_active=True,
        ),
    ]

    session.add_all(plans)
    await session.commit()

    logger.info("Plans seeded successfully")