from .base import TribalAIException

class LLMNotLoadedException(TribalAIException):
    def __init__(self):
        super().__init__(
            status_code=500,
            error="LLM Error",
            message="Llama 3 model is not loaded"
        )