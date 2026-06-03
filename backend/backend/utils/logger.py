"""Structured logging via loguru. Import logger from here everywhere."""

import sys
from loguru import logger
from backend.config import settings


def setup_logger() -> None:
    logger.remove()
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | {message}"
    )
    logger.add(sys.stdout, level=settings.log_level, format=fmt, colorize=True)
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}",
        rotation="50 MB",
        compression="zip",
        enqueue=True,
    )


setup_logger()
