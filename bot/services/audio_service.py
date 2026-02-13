from bot.models.context import JobContext
from bot.exceptions import ProcessingError

from bot.services.beat_mixer import BeatMixer
from bot.services.vocal_processor import VocalProcessor


class AudioService:
    def __init__(self):
        self.beat_mixer = BeatMixer()        
        self.vocal_processor = VocalProcessor()

    async def process(self, ctx: JobContext):
        if not ctx.chosen_style:
            raise ProcessingError("style_not_selected")

        if ctx.chosen_style == "vocal":
            return await self.vocal_processor.process(ctx)

        if ctx.chosen_style in {"rap", "rock", "pop"}:
            return await self.beat_mixer.process(ctx)

        raise ProcessingError("unknown_style")