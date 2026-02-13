from .base import BotError
from .processing import VoiceNotFoundError, ProcessingError
from .limits import DailyLimitExceededError
from .storage import StorageError

__all__ = [
    "BotError",
    "VoiceNotFoundError",
    "ProcessingError",
    "DailyLimitExceededError",
    "StorageError",
]