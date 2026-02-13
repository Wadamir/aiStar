import subprocess
import random
from pathlib import Path

from bot.models.context import JobContext
from bot.exceptions import ProcessingError

BEATS_ROOT = Path("storage/beats")
PROCESSED_ROOT = Path("storage/processed")


class BeatMixer:
    async def process(self, ctx: JobContext):
        beats_dir = BEATS_ROOT / ctx.chosen_style

        if not beats_dir.exists():
            raise ProcessingError("beat_not_found")

        beats = list(beats_dir.glob("*.*"))
        if not beats:
            raise ProcessingError("beat_not_found")

        beat_file = random.choice(beats)

        PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)

        output_path = PROCESSED_ROOT / f"{ctx.voice_path.stem}_mixed.mp3"

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(ctx.voice_path),
            "-stream_loop", "-1",
            "-i", str(beat_file),
            "-filter_complex",
            "[0:a]volume=1.4,highpass=f=90,acompressor=threshold=-18dB:ratio=4[a1];"
            "[1:a]volume=0.6[a2];"
            "[a1][a2]amix=inputs=2:duration=first:dropout_transition=2",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(output_path),
        ]

        process = subprocess.run(cmd, capture_output=True)

        if process.returncode != 0:
            raise ProcessingError("ffmpeg_mix_failed")

        ctx.output_files.append(output_path)