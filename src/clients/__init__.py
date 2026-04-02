import importlib
import os
import sys
from typing import Type

from src.logger import logger

# Get the client name from the environment
client_name = os.getenv("AUTO_UFL_CLIENT_ENV", "none").lower()

if client_name == "none":
    logger.error("No client found in the environment variable")
    sys.exit(1)

else:
    logger.info(f"{client_name} is found in environment variable")

try:
    # Construct the full module path
    module_path = f"src.clients.{client_name}.processor"

    # Dynamically import the module
    processor = importlib.import_module(module_path)

    # Pull class/function into the local namespace
    ExcelProcessor = getattr(processor, "ExcelProcessor")

except (ImportError, AttributeError):
    logger.exception(
        f"Could not load required modules for '{client_name}'. "
        f"Ensure 'clients/{client_name}/processor.py' exists and contains a 'Processor' class."
    )
    sys.exit(1)

__all__ = ["ExcelProcessor"]
