import subprocess
from pathlib import Path

from bot.models.context import JobContext
from bot.exceptions import ProcessingError

PROCESSED_ROOT = Path("storage/processed")


class VocalProcessor:
    async def process(self, ctx: JobContext):
        PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)

        output_path = PROCESSED_ROOT / f"{ctx.voice_path.stem}_vocal.mp3"

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(ctx.voice_path),
            "-af",
            "highpass=f=80, lowpass=f=12000, afftdn, acompressor=threshold=-18dB:ratio=3, loudnorm",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(output_path),
        ]

        process = subprocess.run(cmd, capture_output=True)

        if process.returncode != 0:
            raise ProcessingError("ffmpeg_vocal_failed")

        ctx.output_files.append(output_path)