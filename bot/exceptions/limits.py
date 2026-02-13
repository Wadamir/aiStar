from .base import BotError


class DailyLimitExceededError(BotError):
    """User exceeded daily limit."""