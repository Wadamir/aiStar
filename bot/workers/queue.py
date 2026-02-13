import asyncio
import logging

from bot.models.context import JobContext


class JobQueue:
    def __init__(self):
        self._queue: asyncio.Queue[JobContext | None] = asyncio.Queue()

    async def put(self, ctx: JobContext):
        logging.info(f"Adding job to queue: user_id={ctx.user_id}")
        await self._queue.put(ctx)

    async def get(self) -> JobContext | None:
        logging.info("Waiting for job from queue...")
        return await self._queue.get()

    def task_done(self):
        self._queue.task_done()

    async def shutdown(self):
        await self._queue.put(None)