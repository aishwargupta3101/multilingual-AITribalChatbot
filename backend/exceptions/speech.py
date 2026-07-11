from .base import TribalAIException

class SpeechRecognitionException(TribalAIException):
    def __init__(self):
        super().__init__(
            status_code=500,
            error="Speech Recognition Error",
            message="Speech could not be recognized."
        )