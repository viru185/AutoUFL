from __future__ import annotations

from functools import cache
from pathlib import Path
import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@cache
def _project_table() -> dict:
    pyproject = PROJECT_ROOT / "pyproject.toml"
    with pyproject.open("rb") as handle:
        data = tomllib.load(handle)
    return data.get("project", {})


def get_version() -> str:
    return _project_table().get("version", "0.0.0")


def get_author_record() -> dict:
    authors = _project_table().get("authors", [])
    return authors[0] if authors else {}


def get_project_urls() -> dict:
    return _project_table().get("urls", {})
