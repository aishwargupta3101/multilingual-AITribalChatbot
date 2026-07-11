from .base import TribalAIException

class TranslationException(TribalAIException):
    def __init__(self):
        super().__init__(
            status_code=500,
            error="Translation error",
            message="Translation failed."
        )