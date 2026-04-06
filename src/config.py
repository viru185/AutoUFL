"""
Application configuration constants and helpers.

Values can be overridden via environment variables to keep the code flexible.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _get_bool_env(name: str, default: bool = False) -> bool:
    """Return a boolean env var with permissive parsing."""

    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parents[1]


# Root folder of the repository; handy for building other default paths.
PROJECT_ROOT = get_base_path()

# Load .env ahead of reading os.getenv values.
load_dotenv(PROJECT_ROOT / ".env")

# Logging
LOG_LEVEL = os.getenv("AUTO_UFL_LOG_LEVEL", "INFO")
LOG_TO_CONSOLE = _get_bool_env("AUTO_UFL_LOG_CONSOLE", False)
LOG_ROTATION = os.getenv("AUTO_UFL_LOG_ROTATION", "5 MB")
LOG_RETENTION = os.getenv("AUTO_UFL_LOG_RETENTION", "0")
LOG_PATH = Path(os.getenv("AUTO_UFL_LOG_PATH", PROJECT_ROOT / "autoUFL.log"))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# default dir of file input and output creating on script.
DEFAULT_INPUT_FOLDER = Path(os.getenv("AUTO_UFL_INPUT_DIR", PROJECT_ROOT / "Client Input")).resolve()
DEFAULT_INPUT_FOLDER.mkdir(exist_ok=True)
DEFAULT_OUTPUT_FOLDER = Path(os.getenv("AUTO_UFL_OUTPUT_DIR", PROJECT_ROOT / "CSV UFL Input")).resolve()
DEFAULT_OUTPUT_FOLDER.mkdir(exist_ok=True)

# extension of supported file
SUPPORTED_EXTENSIONS = (".xls", ".xlsx", ".xlsm")

# suffix of after file is processed.
ARCHIVE_SUFFIX_SUCCESS = "_done"
ARCHIVE_SUFFIX_ERROR = "_error"

DEFAULT_TIMESTAMP = os.getenv("AUTO_UFL_DEFAULT_TIMESTAMP", "05:00:00")

ISO_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

# Watchdog -------------------------------------------------------------------
WATCH_POLLING_INTERVAL = float(os.getenv("AUTO_UFL_WATCH_INTERVAL", "1.0"))
WATCH_STABILIZATION_SECONDS = float(os.getenv("AUTO_UFL_FILE_STABILIZE", "1.0"))
