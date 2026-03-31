"""File-based briefing cache — keyed by request-parameter SHA256, TTL-based."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 15 * 60  # 15 minutes
CACHE_DIR = Path(os.environ.get("NEWS_REPORT_CACHE_DIR", Path.home() / ".cache" / "news-report"))


def _ttl() -> int:
    try:
        return int(os.environ.get("NEWS_REPORT_CACHE_TTL", DEFAULT_TTL_SECONDS))
    except (TypeError, ValueError):
        return DEFAULT_TTL_SECONDS


def cache_key(request: dict) -> str:
    """Deterministic SHA256 hash of the request parameters."""
    canonical = json.dumps(request, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def cache_read(key: str) -> dict | None:
    """Return cached briefing if it exists and has not expired, else None."""
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("Corrupt cache file %s, removing", path)
        import contextlib

        with contextlib.suppress(OSError):
            path.unlink(missing_ok=True)
        return None

    stored_at = data.get("_cached_at", 0)
    if time.time() - stored_at > _ttl():
        logger.info("Cache expired for key %s", key[:12])
        return None

    data.pop("_cached_at", None)
    logger.info("Cache hit for key %s", key[:12])
    return data


def cache_write(key: str, briefing: dict) -> None:
    """Persist *briefing* to disk. Failures are logged but never raised."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {**briefing, "_cached_at": time.time()}
        _cache_path(key).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        logger.info("Cache written for key %s", key[:12])
    except OSError:
        logger.warning("Failed to write cache for key %s", key[:12], exc_info=True)
