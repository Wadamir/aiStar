from .base import BotError


class ProcessingError(BotError):
    """
    Audio processing error.
    code — localization key.
    """

    def __init__(self, code: str = "processing_failed"):
        self.code = code
        super().__init__(code)


class VoiceNotFoundError(ProcessingError):
    """
    Voice file was not found.
    """

    def __init__(self):
        super().__init__("voice_not_found")