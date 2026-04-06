"""
Centralized loguru configuration.
"""

from __future__ import annotations

import sys

from loguru import logger

from src.config import LOG_LEVEL, LOG_PATH, LOG_RETENTION, LOG_ROTATION, LOG_TO_CONSOLE


def configure_logger() -> None:
    logger.remove()

    if LOG_TO_CONSOLE:
        logger.add(
            sys.stdout,
            level=LOG_LEVEL,
            colorize=True,
            enqueue=True,
            format=("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " "<level>{level: <8}</level> | {message}"),
        )

    if LOG_PATH:
        logger.add(
            LOG_PATH,
            level=LOG_LEVEL,
            enqueue=True,
            rotation=LOG_ROTATION,
            retention=LOG_RETENTION,
        )


configure_logger()

__all__ = ["logger"]
