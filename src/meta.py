from __future__ import annotations

from importlib import metadata
from pathlib import Path
import sys
import tomllib

PACKAGE_NAME = "autoufl"
_FALLBACK_VERSION = "0.0.0"
_AUTHOR = {
    "name": "Viren Hirpara",
    "email": "viren@virenhirpara.com",
}
_URLS = {
    "Portfolio": "https://www.virenhirpara.com",
    "GitHub": "https://github.com/viru185",
    "LinkedIn": "https://www.linkedin.com/in/hirparaviren/",
}


def get_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[1]


def _version_from_pyproject() -> str | None:
    try:
        pyproject = get_base_path() / "pyproject.toml"
        with pyproject.open("rb") as handle:
            data = tomllib.load(handle)
        return data["project"]["version"]
    except Exception:
        return None


def get_version() -> str:
    file_version = _version_from_pyproject()
    if file_version:
        return file_version
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return _FALLBACK_VERSION


def get_author_record() -> dict:
    return _AUTHOR.copy()


def get_project_urls() -> dict:
    return _URLS.copy()
