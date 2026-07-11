from .base import TribalAIException

class DatabaseConnectionException(TribalAIException):
    def __init__(self):
        super().__init__(
            status_code=500,
            error="Database Connection Error",
            message="Unable to connect to MongoDB."
        )