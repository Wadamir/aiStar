class BotError(Exception):
    """
    Base domain error of the application.
    """

    def __init__(self, message: str):
        super().__init__(message)