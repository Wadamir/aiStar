from pathlib import Path
from bot.config.settings import settings


class StorageService:
    def __init__(self):
        self.base_path = Path(settings.STORAGE_PATH)
        self.voice_path = self.base_path / "voices"
        self.voice_path.mkdir(parents=True, exist_ok=True)

    def build_voice_path(self, file_id: str) -> Path:
        return self.voice_path / f"{file_id}.ogg"