from dataclasses import dataclass, field
from typing import Callable, Optional, Literal
from pathlib import Path

from .stages import JobStage

ProgressCallback = Callable[[JobStage, dict], None]

@dataclass
class JobContext:
    # === Identification ===
    user_id: int
    user_first_name: Optional[str] = None
    user_username: Optional[str] = None
    locale: Optional[str] = None
    song_id: Optional[int] = None

    # === Input ===
    voice_msg_id: Optional[int] = None
    voice_path: Optional[Path] = None

    # === Processing params ===
    chosen_style: Optional[str] = None
    chosen_bitrate: Optional[int] = None

    # === Runtime state ===
    status: Literal["pending", "processing", "success", "failed"] = "pending"

    # === Output ===
    output_files: list[Path] = field(default_factory=list)

    # === Metrics ===
    estimated_size_mb: Optional[float] = None
    real_size_mb: Optional[float] = None
    processing_time_sec: Optional[float] = None

    # === Errors ===
    fallback_reason: Optional[str] = None
    error_message: Optional[str] = None

    # === Progress ===
    on_progress: Optional[ProgressCallback] = None
