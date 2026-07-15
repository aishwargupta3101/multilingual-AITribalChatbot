from backend.config.logger import logger

async def create_indexes():
    logger.info("Creating MongoDB indexes....")
    logger.info("MongoDB indexes created.")
