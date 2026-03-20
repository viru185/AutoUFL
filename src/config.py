"""
Application configuration constants and helpers.

Values can be overridden via environment variables to keep the code flexible.
"""

from __future__ import annotations

import os
from pathlib import Path

# Root folder of the repository; handy for building other default paths.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Logging --------------------------------------------------------------------
LOG_LEVEL = os.getenv("AUTO_UFL_LOG_LEVEL", "INFO")
LOG_TO_CONSOLE = os.getenv("AUTO_UFL_LOG_CONSOLE", "true").lower() == "true"
LOG_PATH = os.getenv("AUTO_UFL_LOG_PATH")  # Optional log file

# Data processing -------------------------------------------------------------
SHEET_NAME = os.getenv("AUTO_UFL_SHEET_NAME", "P&B")

DEFAULT_INPUT_FOLDER = Path(os.getenv("AUTO_UFL_INPUT_DIR", PROJECT_ROOT / "data" / "incoming"))
DEFAULT_OUTPUT_FOLDER = Path(os.getenv("AUTO_UFL_OUTPUT_DIR", PROJECT_ROOT / "data" / "normalized"))

SUPPORTED_EXTENSIONS = (".xls", ".xlsx", ".xlsm")

ARCHIVE_SUFFIX_SUCCESS = "_done"
ARCHIVE_SUFFIX_ERROR = "_error"

ISO_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Month labels seen in the workbook (Apr-25, Mar-2026, etc.)
MONTH_FORMATS = (
    "%b-%y",
    "%b-%Y",
    "%b %y",
    "%b %Y",
    "%B-%y",
    "%B-%Y",
)

# Watchdog -------------------------------------------------------------------
WATCH_POLLING_INTERVAL = float(os.getenv("AUTO_UFL_WATCH_INTERVAL", "1.0"))
WATCH_STABILIZATION_SECONDS = float(os.getenv("AUTO_UFL_FILE_STABILIZE", "1.0"))
