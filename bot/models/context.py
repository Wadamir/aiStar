from dataclasses import dataclass, field
from typing import Callable, Optional, Literal
from pathlib import Path

from .stages import JobStage

ProgressCallback = Callable[[JobStage, dict], None]

@dataclass
class JobContext:
    user_id: int

    # Song
    song_id: Optional[int] = None

    # voice
    voice_msg_id: Optional[int] = None
    voice_path: Optional[Path] = None

    # processing
    chosen_style: Optional[str] = None
    chosen_bitrate: Optional[int] = None

    #result
    status: Literal["pending", "processing", "success", "failed"] = "pending"
    output_files: list[Path] = field(default_factory=list)

    # metrics
    estimated_size_mb: Optional[float] = None
    real_size_mb: Optional[float] = None
    processing_time_sec: Optional[float] = None

    #errors
    fallback_reason: Optional[str] = None
    error_message: Optional[str] = None

    #stages
    on_progress: Optional[ProgressCallback] = None
