from pathlib import Path
from loguru import logger
import shutil


class JobPipeline:
    async def run(self, ctx):
        # Do not catch exceptions here — let them bubble up to Worker
        await self.fetch(ctx)
        await self.process(ctx)
        await self.save(ctx)

    async def fetch(self, ctx):
        logger.info(f"Fetching voice file: {ctx.voice_path}")

        if ctx.voice_path is None:
            raise ValueError("voice_path is None")

        if not isinstance(ctx.voice_path, Path):
            raise TypeError("voice_path must be a pathlib.Path instance")

        if not ctx.voice_path.exists():
            raise FileNotFoundError(f"Voice file not found: {ctx.voice_path}")

    async def process(self, ctx):
        logger.info("Processing voice...")

        output_dir = Path("storage/processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{ctx.voice_path.stem}_processed.ogg"

        # If copy fails, exception will propagate
        shutil.copy(ctx.voice_path, output_file)

        ctx.output_files.append(output_file)

    async def save(self, ctx):
        logger.info("Saving results...")

        if not ctx.output_files:
            raise RuntimeError("No output files were generated during processing")

        logger.success(f"Generated file: {ctx.output_files[0]}")