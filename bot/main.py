import asyncio
from loguru import logger

from bot.setup import setup_bot
from bot.db.init import init_db
from bot.utils.logger import setup_logger

from bot.workers.worker import Worker
from bot.pipeline.job_pipeline import JobPipeline


async def main():
    setup_logger()
    logger.info("Starting AI Star Bot")

    await init_db()
    logger.info("Database initialized")

    bot, dp, job_queue = setup_bot()

    pipeline = JobPipeline()
    worker = Worker(bot, job_queue, pipeline)
    asyncio.create_task(worker.run())

    try:
        logger.info("Starting polling")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())