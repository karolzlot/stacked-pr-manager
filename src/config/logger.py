import sys

from loguru import logger

logger_format_stderr = (
    "<green>{time:HH:mm:ss}</green> " "<level>{level: <8}</level>| " "{message}"
)
logger_format_file = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)
logger.remove()
logger.add(sys.stderr, format=logger_format_stderr, level="DEBUG")
logger.add("logs/file_{time}.log", format=logger_format_file, level="TRACE")
