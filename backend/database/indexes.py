from backend.config.logger import logger
from backend.database.connection import mongodb


async def create_indexes():
    logger.info("Creating MongoDB indexes....")
    database = mongodb.database
    if database is None:
        logger.warning("MongoDB database unavailable; skipping index creation.")
        return
    await database["video_lessons"].create_index(
        [("video_id", 1), ("level", 1), ("language", 1), ("cache_version", 1)],
        unique=True,
        name="video_lesson_cache_lookup_unique",
    )
    logger.info("MongoDB indexes created.")
