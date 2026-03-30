"""
Centralized loguru configuration.
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from src.config import LOG_LEVEL, LOG_PATH, LOG_TO_CONSOLE


def configure_logger() -> None:
    logger.remove()

    if LOG_TO_CONSOLE:
        logger.add(
            sys.stdout,
            level=LOG_LEVEL,
            colorize=True,
            enqueue=True,
        )

    if LOG_PATH:
        logger.add(
            LOG_PATH,
            level=LOG_LEVEL,
            enqueue=True,
            rotation="5 MB",
            retention=0,
        )


configure_logger()

__all__ = ["logger"]
