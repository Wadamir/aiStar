import subprocess
import random
import json

from pathlib import Path
from loguru import logger

from bot.models.context import JobContext
from bot.exceptions import ProcessingError

from bot.config.settings import settings



class BeatMixer:
    def __init__(self):
        self.beats_root = Path(settings.BEATS_PATH)
        self.processed_root = Path(settings.PROCESSED_PATH)

    # --------------------------------------------------
    # Utility: get audio duration via ffprobe
    # --------------------------------------------------
    def _get_duration(self, path: Path) -> float:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise ProcessingError("ffprobe_failed")

        data = json.loads(result.stdout)
        return float(data["format"]["duration"])

    # --------------------------------------------------
    # Filter builder (structured beat: intro | main | outro)
    # --------------------------------------------------
    def _build_filter(
        self,
        intro_sec: float,
        main_duration: float,
        main_needed_duration: float,
        outro_sec: float,
        beat_duration: float,
        vocal_duration: float,
        fade_out_start: float,
        loop_main: bool,
    ) -> str:

        intro_end = intro_sec
        main_start = intro_sec
        main_end = intro_sec + main_duration
        outro_start = beat_duration - outro_sec

        # If main must be looped, we trim full main and loop later
        if loop_main:
            main_trim = f"[1:a]atrim=start={main_start}:end={main_end},asetpts=PTS-STARTPTS[main_raw];"
            main_loop = f"[main_raw]aloop=loop=-1:size=0,atrim=duration={main_needed_duration}[main];"
        else:
            main_trim = f"[1:a]atrim=start={main_start}:end={main_start + main_needed_duration},asetpts=PTS-STARTPTS[main];"
            main_loop = ""

        return f"""
        [1:a]atrim=start=0:end={intro_end},asetpts=PTS-STARTPTS[intro];
        {main_trim}
        {main_loop}
        [1:a]atrim=start={outro_start}:end={beat_duration},asetpts=PTS-STARTPTS[outro];

        [main]volume=0.6[main_quiet];

        [0:a]adelay={int(intro_sec*1000)}|{int(intro_sec*1000)},
            highpass=f=90,
            acompressor=threshold=-20dB:ratio=4:makeup=5,
            volume=1.8[vocal];

        [main_quiet][vocal]sidechaincompress=threshold=0.05:ratio=8[main_sc];

        [main_sc][vocal]amix=inputs=2:duration=first:dropout_transition=2[mixed_main];

        [intro][mixed_main][outro]concat=n=3:v=0:a=1[preout];

        [preout]afade=t=out:st={fade_out_start}:d={outro_sec},
            loudnorm=I=-16:LRA=11:TP=-1.5[final]
        """

    # --------------------------------------------------
    # Beat structure helper
    # --------------------------------------------------
    def _prepare_beat_segments(
        self,
        beat_duration: float,
        intro_sec: float,
        outro_sec: float,
        vocal_duration: float,
    ) -> dict:
        """
        Calculate beat structure: intro | main | outro.
        If vocal is longer than main part, main should be looped later.
        """

        # Ensure intro/outro do not exceed beat duration
        intro_sec = min(intro_sec, beat_duration)
        outro_sec = min(outro_sec, max(0.0, beat_duration - intro_sec))

        # Raw main duration inside original beat
        main_duration = max(0.0, beat_duration - intro_sec - outro_sec)

        if main_duration <= 0:
            # Degenerate case: no main section
            return {
                "intro_sec": intro_sec,
                "main_duration": 0.0,
                "main_needed_duration": vocal_duration,
                "outro_sec": outro_sec,
                "loop_main": True,
                "total_duration": intro_sec + vocal_duration + outro_sec,
            }

        # Determine if we need to loop main
        if vocal_duration > main_duration:
            loop_main = True
            main_needed_duration = vocal_duration
        else:
            loop_main = False
            main_needed_duration = vocal_duration

        total_duration = intro_sec + main_needed_duration + outro_sec

        return {
            "intro_sec": intro_sec,
            "main_duration": main_duration,
            "main_needed_duration": main_needed_duration,
            "outro_sec": outro_sec,
            "loop_main": loop_main,
            "total_duration": total_duration,
        }

    # --------------------------------------------------
    # Main process
    # --------------------------------------------------
    async def process(self, ctx: JobContext):

        if not ctx.voice_path:
            raise ProcessingError("voice_not_found")

        beats_dir = self.beats_root / ctx.chosen_style

        if not beats_dir.exists():
            raise ProcessingError("beat_not_found")

        beats = list(beats_dir.glob("*.mp3"))
        if not beats:
            raise ProcessingError("beat_not_found")

        beat_file = random.choice(beats)
        logger.info(f"Selected beat {beat_file} for user_id={ctx.user_id}")

        self.processed_root.mkdir(parents=True, exist_ok=True)

        # -----------------------------------
        # 1. Get vocal duration
        # -----------------------------------
        voice_duration = self._get_duration(ctx.voice_path)
        logger.info(f"Voice duration: {voice_duration:.2f} sec for user_id={ctx.user_id}")

        # intro_sec = 4
        # outro_sec = 4

        # total_duration = voice_duration + intro_sec
        # fade_out_start = total_duration - outro_sec

        # -----------------------------------
        # 2. Get beat duration
        # -----------------------------------        
        beat_duration = self._get_duration(beat_file)
        logger.info(f"Beat duration: {beat_duration:.2f} sec for user_id={ctx.user_id}")

        # -----------------------------------
        # 3. Get intro and outro durations based on beat json or defaults
        # -----------------------------------  
        beat_json = beat_file.with_suffix(".json")
        if beat_json.exists():
            try:
                with open(beat_json, "r") as f:
                    data = json.load(f)
                    intro_sec = data.get("intro_sec", min(8, beat_duration * 0.25))
                    outro_sec = data.get("outro_sec", min(8, beat_duration * 0.25))
            except Exception as e:
                logger.warning(f"Failed to read beat JSON {beat_json}: {e}")
                intro_sec = min(8, beat_duration * 0.25)
                outro_sec = min(8, beat_duration * 0.25)
        else:
            intro_sec = min(8, beat_duration * 0.25)
            outro_sec = min(8, beat_duration * 0.25)

        # -----------------------------------
        # 5. Prepare beat structure (intro | main | outro)
        # -----------------------------------
        structure = self._prepare_beat_segments(
            beat_duration=beat_duration,
            intro_sec=intro_sec,
            outro_sec=outro_sec,
            vocal_duration=voice_duration,
        )

        intro_sec = structure["intro_sec"]
        main_duration = structure["main_duration"]
        main_needed_duration = structure["main_needed_duration"]
        outro_sec = structure["outro_sec"]
        total_duration = structure["total_duration"]
        loop_main = structure["loop_main"]

        logger.info(
            f"Beat structure for user_id={ctx.user_id}: "
            f"intro={intro_sec:.2f}, "
            f"main={main_duration:.2f}, "
            f"main_needed={main_needed_duration:.2f}, "
            f"loop_main={loop_main}, "
            f"outro={outro_sec:.2f}, "
            f"total={total_duration:.2f}"
        )

        fade_out_start = total_duration - outro_sec

        # -----------------------------------
        # 6. Build structured filter
        # -----------------------------------
        filter_complex = self._build_filter(
            intro_sec=intro_sec,
            main_duration=main_duration,
            main_needed_duration=main_needed_duration,
            outro_sec=outro_sec,
            beat_duration=beat_duration,
            vocal_duration=voice_duration,
            fade_out_start=fade_out_start,
            loop_main=loop_main,
        )

        # -----------------------------------
        # 7. Output file name
        # -----------------------------------
        safe_name = (
            ctx.user_first_name
            or ctx.user_username
            or f"user_{ctx.user_id}"
        )

        output_path = self.processed_root / f"{safe_name}_AIStar_{ctx.chosen_style}.mp3"

        # -----------------------------------
        # 8. FFmpeg command
        # -----------------------------------
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(ctx.voice_path),
            "-i", str(beat_file),
            "-filter_complex", filter_complex,
            "-map", "[final]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(output_path),
        ]

        process = subprocess.run(cmd, capture_output=True)

        if process.returncode != 0:
            raise ProcessingError("ffmpeg_mix_failed")

        ctx.output_files.append(output_path)

        return output_path