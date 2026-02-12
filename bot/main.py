import asyncio
from loguru import logger

from bot.setup import setup_bot
from bot.db.init import init_db
from bot.utils.logger import setup_logger


async def main():
    setup_logger()
    logger.info("Starting AI Star Bot")

    await init_db()
    logger.info("Database initialized")

    bot, dp = setup_bot()

    try:
        logger.info("Starting polling")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())