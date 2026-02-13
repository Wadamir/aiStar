from loguru import logger
from aiogram import Bot
from aiogram.types import FSInputFile

from bot.workers.queue import JobQueue
from bot.pipeline.job_pipeline import JobPipeline
from bot.exceptions import BotError
from bot.i18n.loader import get_text as _


class Worker:
    def __init__(self, bot: Bot, queue: JobQueue, pipeline: JobPipeline):
        self.bot = bot
        self.queue = queue
        self.pipeline = pipeline

    async def run(self):
        logger.info("Worker started")

        while True:
            logger.info("Worker waiting for job...")
            ctx = await self.queue.get()

            if ctx is None:
                logger.info("Worker received shutdown signal")
                break

            logger.info(f"Worker got job for user_id={ctx.user_id}")

            try:
                await self._handle_job(ctx)

            except BotError as e:
                await self._handle_known_error(ctx, e)

            except Exception as e:
                await self._handle_unexpected_error(ctx, e)

            finally:
                self.queue.task_done()

    async def _handle_job(self, ctx):
        ctx.status = "processing"

        await self._update_status(ctx, "processing_started")

        await self.pipeline.run(ctx)

        ctx.status = "success"
        logger.success(f"Job completed for user_id={ctx.user_id}")

        if ctx.output_files:
            audio_file = FSInputFile(ctx.output_files[0])
            await self.bot.send_audio(
                chat_id=ctx.user_id,
                audio=audio_file
            )

        await self._update_status(ctx, "processing_finished")

    async def _handle_known_error(self, ctx, error: BotError):
        ctx.status = "failed"
        ctx.error_message = str(error)

        logger.warning(
            f"Business error for user_id={ctx.user_id}: {error}"
        )

        # Use error code from exception to determine which message to show the user
        code = getattr(error, "code", "processing_failed")

        await self._update_status(ctx, code)

    async def _handle_unexpected_error(self, ctx, error: Exception):
        ctx.status = "failed"
        ctx.error_message = str(error)

        logger.exception(
            f"Unexpected error for user_id={ctx.user_id}"
        )

        await self._update_status(ctx, "internal_error")

    async def _update_status(self, ctx, code: str):
        """
        Update the status message for the user based on the provided code.
        The code corresponds to a key in the i18n translations.
        """
        if not ctx.voice_msg_id or not ctx.locale:
            return

        text = _(code, locale=ctx.locale)

        await self.bot.edit_message_text(
            chat_id=ctx.user_id,
            message_id=ctx.voice_msg_id,
            text=text
        )