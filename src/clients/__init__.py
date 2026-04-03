from __future__ import annotations

from typing import Type

from src.logger import logger

from .registry import CLIENT_REGISTRY


def get_processor_class(client_name: str | None = None) -> Type:
    """
    Resolve the ExcelProcessor class for the requested client.

    When client_name is None we fall back to the build default.
    """

    processor_cls = CLIENT_REGISTRY.load_processor_class(client_name)
    resolved = client_name or CLIENT_REGISTRY.default_client() or "unknown"
    logger.info(f"Using ExcelProcessor for client {resolved}")
    return processor_cls


def list_available_clients() -> tuple[str, ...]:
    """Return the client names packaged with the current build."""

    return CLIENT_REGISTRY.available_clients()


ExcelProcessor = get_processor_class()

__all__ = ["ExcelProcessor", "get_processor_class", "list_available_clients", "CLIENT_REGISTRY"]
