"""RSSHub adapter — fetches real RSS feeds via a public (or self-hosted) RSSHub instance."""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import UTC, datetime
from time import mktime

import feedparser
import httpx

logger = logging.getLogger(__name__)

MAX_CANDIDATES_PER_FETCH = 50

# Maps topic keywords (lowercase) → list of RSSHub routes to query.
# Each route is relative to the RSSHub base URL.
TOPIC_ROUTE_MAP: dict[str, list[str]] = {
    "ai": ["/hackernews/best", "/36kr/newsflashes"],
    "open source": ["/github/trending/daily", "/hackernews/best"],
    "tech": ["/hackernews/best", "/36kr/newsflashes"],
    "startup": ["/36kr/newsflashes"],
    "python": ["/github/trending/daily/python"],
    "machine learning": ["/arxiv/cs.AI"],
    "security": ["/hackernews/best"],
}

# Fallback routes when no specific mapping exists for a topic.
DEFAULT_ROUTES = ["/hackernews/best"]


def _rsshub_base_url() -> str:
    return os.environ.get("RSSHUB_BASE_URL", "https://rsshub.app").rstrip("/")


def _parse_published(entry: dict) -> datetime:
    """Best-effort extraction of a publish datetime from a feedparser entry."""
    for field in ("published_parsed", "updated_parsed"):
        parsed = entry.get(field)
        if parsed is not None:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=UTC)
            except (TypeError, ValueError, OverflowError):
                continue
    return datetime.now(UTC)


def _entry_id(entry: dict, source_id: str, route: str) -> str:
    """Derive a stable unique ID for a feed entry."""
    raw = entry.get("id") or entry.get("link") or entry.get("title", "")
    return hashlib.sha256(f"{source_id}:{route}:{raw}".encode()).hexdigest()[:16]


class RSSHubAdapter:
    """Adapter that fetches live data from an RSSHub instance."""

    def __init__(self, source: dict) -> None:
        self.source = source
        self.source_id: str = source["id"]
        self._base_url = _rsshub_base_url()
        self._client = httpx.Client(
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
            follow_redirects=True,
        )

    # --------------------------------------------------------------------- #
    # SourceAdapter protocol
    # --------------------------------------------------------------------- #

    def fetch(self, topic: str, summary_style: str, now: datetime | None = None) -> list[dict]:
        """Fetch candidates from RSSHub routes matching *topic*."""
        now = now or datetime.now(UTC)
        routes = TOPIC_ROUTE_MAP.get(topic.lower(), DEFAULT_ROUTES)
        candidates: list[dict] = []

        for route in routes:
            try:
                items = self._fetch_route(route, topic, summary_style, now)
                candidates.extend(items)
            except Exception:
                logger.warning("RSSHub fetch failed for route %s, skipping", route, exc_info=True)

        return candidates[:MAX_CANDIDATES_PER_FETCH]

    def ping(self) -> bool:
        """Check if the RSSHub instance is reachable."""
        try:
            resp = self._client.get(self._base_url, timeout=5.0)
            return resp.status_code < 500
        except Exception:
            return False

    # --------------------------------------------------------------------- #
    # Internal
    # --------------------------------------------------------------------- #

    def _fetch_route(self, route: str, topic: str, summary_style: str, now: datetime) -> list[dict]:
        url = f"{self._base_url}{route}"
        logger.info("Fetching RSSHub route %s for topic %r", route, topic)

        resp = self._client.get(url)
        resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        candidates: list[dict] = []

        for entry in feed.entries:
            published_at = _parse_published(entry)

            title = entry.get("title", "").strip()
            if not title:
                continue

            link = entry.get("link", "")
            summary_text = entry.get("summary", "") or entry.get("description", "")
            if summary_style == "headline_only":
                summary_text = title
            elif summary_style == "concise" and len(summary_text) > 300:
                summary_text = summary_text[:297] + "..."

            candidates.append(
                {
                    "id": _entry_id(entry, self.source_id, route),
                    "title": title,
                    "source": self.source_id,
                    "source_name": self.source.get("name", "RSSHub"),
                    "content_type": "article",
                    "url": link,
                    "published_at": published_at,
                    "tags": _extract_tags(entry, topic),
                    "angles": [topic.lower()],
                    "summary": summary_text,
                    "source_meta": self.source,
                }
            )

        return candidates

    def __del__(self) -> None:
        import contextlib

        with contextlib.suppress(Exception):
            self._client.close()


def _extract_tags(entry: dict, topic: str) -> list[str]:
    """Pull tags from a feedparser entry, falling back to topic."""
    tags = []
    for tag_info in entry.get("tags", []):
        term = tag_info.get("term", "").strip()
        if term:
            tags.append(term.lower())
    if not tags:
        tags = [topic.lower()]
    return tags
