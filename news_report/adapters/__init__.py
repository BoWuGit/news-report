"""Adapter package — SourceAdapter Protocol and registry."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Protocol, runtime_checkable

from news_report.adapters.mock import StaticSourceAdapter
from news_report.adapters.rsshub import RSSHubAdapter

logger = logging.getLogger(__name__)


@runtime_checkable
class SourceAdapter(Protocol):
    """Protocol that every source adapter must satisfy."""

    source_id: str

    def fetch(self, topic: str, summary_style: str, now: datetime | None = None) -> list[dict]:
        """Fetch candidate items for *topic*. Returns a list of candidate dicts."""
        ...

    def ping(self) -> bool:
        """Return True if the upstream source is reachable (timeout 5 s)."""
        ...


# Maps source IDs to adapter *classes* (not instances).
# Sources not in this map fall back to StaticSourceAdapter.
ADAPTER_MAP: dict[str, type] = {}


def _register_builtin_adapters() -> None:
    """Lazily populate ADAPTER_MAP with adapters that ship with news-report."""
    if ADAPTER_MAP:
        return

    ADAPTER_MAP["rsshub"] = RSSHubAdapter


def build_adapter_registry(sources: list[dict]) -> dict[str, SourceAdapter]:
    """Build a source-id → adapter-instance mapping.

    Real adapters are used when available; otherwise StaticSourceAdapter is used
    as a mock fallback.
    """
    _register_builtin_adapters()

    registry: dict[str, SourceAdapter] = {}
    for source in sources:
        sid = source["id"]
        adapter_cls = ADAPTER_MAP.get(sid)
        if adapter_cls is not None:
            registry[sid] = adapter_cls(source)
            logger.debug("Using real adapter %s for source %s", adapter_cls.__name__, sid)
        else:
            registry[sid] = StaticSourceAdapter(source)
            logger.debug("Using mock fallback for source %s", sid)
    return registry
