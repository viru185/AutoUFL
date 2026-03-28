from __future__ import annotations

from importlib import metadata

PACKAGE_NAME = "autoufl"
_FALLBACK_VERSION = "1.0.0"
_AUTHOR = {
    "name": "Viren Hirpara",
    "email": "viren@virenhirpara.com",
}
_URLS = {
    "Portfolio": "https://www.virenhirpara.com",
    "GitHub": "https://github.com/viru185",
    "LinkedIn": "https://www.linkedin.com/in/hirparaviren/",
}


def get_version() -> str:
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return _FALLBACK_VERSION


def get_author_record() -> dict:
    return _AUTHOR.copy()


def get_project_urls() -> dict:
    return _URLS.copy()
