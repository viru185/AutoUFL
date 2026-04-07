"""
Centralized loguru configuration.
"""

from __future__ import annotations

import sys
from pprint import pformat

from loguru import logger

from src.config import LOG_LEVEL, LOG_PATH, LOG_RETENTION, LOG_ROTATION, LOG_TO_CONSOLE

# Separate configs for each handler

CONSOLE_LOG_CONFIG = {
    "sink": sys.stdout,
    "level": LOG_LEVEL,
    "colorize": True,
    "enqueue": True,
    "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " "<level>{level: <8}</level> | {message}",
}

if LOG_LEVEL == "DEBUG":
    CONSOLE_LOG_CONFIG.pop("format")

FILE_LOG_CONFIG = {
    "sink": LOG_PATH,
    "level": LOG_LEVEL,
    "enqueue": True,
    "rotation": LOG_ROTATION,
    "retention": LOG_RETENTION,
}


def configure_logger() -> None:
    logger.remove()

    if LOG_TO_CONSOLE:
        logger.add(**CONSOLE_LOG_CONFIG)
        logger.info("console logging enabled")
        logger.debug(f"console log config:\n{pformat(CONSOLE_LOG_CONFIG)}")

    if LOG_PATH:
        logger.add(**FILE_LOG_CONFIG)
        logger.info(f"file logging enabled: {LOG_PATH}")
        logger.debug(f"file log config:\n{pformat(FILE_LOG_CONFIG)}")


configure_logger()

__all__ = ["logger"]
