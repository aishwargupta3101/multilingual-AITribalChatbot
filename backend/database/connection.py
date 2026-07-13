from backend.config.logger import logger

class DatabaseConnection:
    def connect(self):
        logger.info("Database connection initialized.")
    def disconnect(self):
        logger.info("Database connection closed")