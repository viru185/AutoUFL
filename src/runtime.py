from __future__ import annotations

from datetime import datetime, time
from functools import cache

from src.config import DEFAULT_TIMESTAMP


@cache
def _parsed_default_time() -> time | None:
    text = DEFAULT_TIMESTAMP.strip()
    if not text:
        return None
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"):
        try:
            return datetime.strptime(text, fmt).time().replace(microsecond=0)
        except ValueError:
            continue
    return None


def processed_timestamp(base: datetime | None = None) -> datetime:
    reference = base or datetime.now()
    override = _parsed_default_time()
    if override is None:
        return reference
    return datetime.combine(reference.date(), override)
