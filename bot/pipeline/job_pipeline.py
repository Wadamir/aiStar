from loguru import logger

from bot.services.audio_service import AudioService
from bot.exceptions import VoiceNotFoundError, ProcessingError


class JobPipeline:
    def __init__(self):
        self.audio_service = AudioService()

    async def run(self, ctx):
        logger.info(f"Running pipeline for user_id={ctx.user_id}, style={ctx.chosen_style}")
        await self.fetch(ctx)
        logger.info(f"Voice file found for user_id={ctx.user_id}, processing...")
        await self.process(ctx)
        logger.info(f"Audio processing completed for user_id={ctx.user_id}, saving output...")
        await self.save(ctx)
        logger.info(f"Pipeline completed for user_id={ctx.user_id}")

    async def fetch(self, ctx):
        if not ctx.voice_path or not ctx.voice_path.exists():
            raise VoiceNotFoundError()

    async def process(self, ctx):
        await self.audio_service.process(ctx)

    async def save(self, ctx):
        if not ctx.output_files:
            raise ProcessingError("no_output_generated")
        logger.info(f"Output files saved for user_id={ctx.user_id}: {ctx.output_files}")    