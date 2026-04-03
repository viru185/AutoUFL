
from __future__ import annotations

import importlib
import json
import os
import pkgutil
from importlib import util
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Type

from src.logger import logger

MANIFEST_NAME = "client_manifest.json"
CLIENTS_PACKAGE = "src.clients"


@dataclass(frozen=True)
class ClientManifest:
    """Represents the configuration baked into a PyInstaller build."""

    enabled_clients: tuple[str, ...]
    default_client: str | None
    multi_client: bool

    @classmethod
    def from_mapping(cls, mapping: dict) -> "ClientManifest":
        enabled = tuple(mapping.get("enabled_clients", ()))
        default = mapping.get("default_client")
        multi = bool(mapping.get("multi_client", False))
        return cls(enabled_clients=enabled, default_client=default, multi_client=multi)

    @property
    def first_client(self) -> str | None:
        return self.enabled_clients[0] if self.enabled_clients else None


def _load_manifest_file() -> ClientManifest | None:
    """Attempt to read the manifest that the build step injects."""

    try:
        manifest_resource = resources.files("src").joinpath(MANIFEST_NAME)
    except ModuleNotFoundError:
        manifest_resource = None

    if manifest_resource:
        with resources.as_file(manifest_resource) as resource_path:
            if resource_path.exists():
                return ClientManifest.from_mapping(json.loads(resource_path.read_text()))

    # Fallback to local build artifacts (useful for dev runs outside PyInstaller)
    fallback_path = Path("build") / MANIFEST_NAME
    if fallback_path.exists():
        return ClientManifest.from_mapping(json.loads(fallback_path.read_text()))

    return None


def _discover_clients_from_sources() -> tuple[str, ...]:
    """Inspect the package to find available client subpackages."""

    try:
        package = importlib.import_module(CLIENTS_PACKAGE)
    except ImportError:
        return ()

    discovered: list[str] = []
    for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
        if not is_pkg or name.startswith("__"):
            continue

        module_name = f"{CLIENTS_PACKAGE}.{name}.processor"
        spec = util.find_spec(module_name)
        if spec is None:
            continue

        discovered.append(name)

    return tuple(sorted(discovered))


class ClientRegistry:
    """Central registry responsible for loading ExcelProcessor classes."""

    def __init__(self, manifest: ClientManifest | None = None):
        self._manifest = manifest or _load_manifest_file() or self._build_fallback_manifest()
        self._client_lookup = {client.lower(): client for client in self._manifest.enabled_clients}
        self._available = set(self._client_lookup.keys())

    def _build_fallback_manifest(self) -> ClientManifest:
        discovered = _discover_clients_from_sources()
        env_default = os.getenv("AUTO_UFL_CLIENT_ENV")

        def _match_default(name: str | None) -> str | None:
            if not name:
                return None
            for client in discovered:
                if client.lower() == name.lower():
                    return client
            return None

        matched_default = _match_default(env_default) or (discovered[0] if discovered else None)

        return ClientManifest(
            enabled_clients=discovered,
            default_client=matched_default,
            multi_client=True,
        )

    def available_clients(self) -> tuple[str, ...]:
        return self._manifest.enabled_clients

    def is_multi_client(self) -> bool:
        return self._manifest.multi_client

    def default_client(self) -> str | None:
        default = self._manifest.default_client
        if default and default.lower() in self._client_lookup:
            return self._client_lookup[default.lower()]
        return self._manifest.first_client

    def has_client(self, client_name: str) -> bool:
        return client_name.lower() in self._available

    def load_processor_class(self, client_name: str | None = None) -> Type:
        target = client_name or self.default_client()
        if not target:
            raise RuntimeError("No client available in this build. Please rebuild with at least one client.")

        normalized = target.lower()
        if normalized not in self._available:
            raise ValueError(f"Client '{client_name}' is not bundled with this build.")

        canonical_name = self._client_lookup[normalized]
        module_name = f"{CLIENTS_PACKAGE}.{canonical_name}.processor"

        try:
            module = importlib.import_module(module_name)
            processor_cls = getattr(module, "ExcelProcessor")
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"Unable to load ExcelProcessor for {normalized}")
            raise RuntimeError(f"Failed to load processor for '{normalized}'") from exc

        return processor_cls


CLIENT_REGISTRY = ClientRegistry()
