import sys

from loguru import logger

from src.config import LOG_LEVEL, LOG_TO_CONSOL


def init_loguru() -> None:

    # Remove the default logger
    logger.remove()

    # Add consol logger if LOG_TO_CONSOL is True
    if LOG_TO_CONSOL:
        logger.add(
            sys.stdout,
            level=LOG_LEVEL,
            colorize=True,
        )


init_loguru()
