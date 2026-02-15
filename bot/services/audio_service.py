from bot.models.context import JobContext
from bot.exceptions import ProcessingError

from bot.services.beat_mixer import BeatMixer
from bot.services.vocal_processor import VocalProcessor
from bot.services.ai_processor import AiProcessor


class AudioService:
    def __init__(self):
        self.beat_mixer = BeatMixer()        
        self.vocal_processor = VocalProcessor()
        self.ai_processor = AiProcessor()
    async def process(self, ctx: JobContext):
        if not ctx.chosen_style:
            raise ProcessingError("style_not_selected")

        if ctx.chosen_style == "vocal":
            return await self.vocal_processor.process(ctx)
        
        if ctx.chosen_style == "ai_vocal":
            return await self.ai_processor.process(ctx)  # For now, using the same vocal processor. Can be replaced with a different one if needed.

        if ctx.chosen_style == "lofi":
            # await self.ai_processor.process(ctx)  # For now, using the same AI processor. Can be replaced with a different one if needed.
            # ctx.voice_path = ctx.output_files[-1]  # Use the AI-processed vocal as input for the beat mixer.
            
            return await self.beat_mixer.process(ctx)  # Mix the AI-processed vocal with a beat. This is a simple approach; ideally, we would want to use a different beat

        if ctx.chosen_style in {"rap", "rock", "pop"}:
            return await self.beat_mixer.process(ctx)

        raise ProcessingError("unknown_style")