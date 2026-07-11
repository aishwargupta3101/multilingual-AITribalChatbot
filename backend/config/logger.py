from loguru import logger
from pathlib import Path
import sys

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    enqueue=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> |"
            "<level>{level}</level> |"
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> |"
            "{message}"
)
logger.add(
    LOG_DIR /"app.log",
    rotation="10MB",
    retention="10days",
    level="INFO",
    enqueue=True
)
logger.add(
    LOG_DIR / "error.log",
    rotation="10 MB",
    retention="30 days",
    level="ERROR",
    enqueue=True
)
logger.add(
    LOG_DIR /"access.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO",
    filter=lambda record: "ACCESS" in record["message"]
)