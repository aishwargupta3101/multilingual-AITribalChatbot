from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
logger.add(
    "logs/backend.log",
    rotation="10MB",
    retention="10days",
    level="INFO"
)
__all__  =["logger"]