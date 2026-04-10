"""Static/mock source adapter backed by local templates."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

SOURCE_ITEM_TEMPLATES = {
    "podwise-cli": [
        {
            "title_template": "{topic}: podcast workflow for agent-native briefings",
            "content_type": "podcast",
            "days_ago": 2,
            "tags": ["agent tools", "audio", "workflow"],
            "angles": ["podcast", "summary", "agent"],
            "summary_seed": "Turns long-form audio into structured notes, summaries, and reusable agent context.",
        },
        {
            "title_template": "{topic}: transcript-to-briefing pipeline with MCP support",
            "content_type": "transcript",
            "days_ago": 7,
            "tags": ["mcp", "transcript", "developer workflows"],
            "angles": ["mcp", "transcript", "developer workflows"],
            "summary_seed": "Shows how audio content can be normalized into outputs a user agent can consume directly.",
        },
    ],
    "readwise-cli": [
        {
            "title_template": "{topic}: saved-reading export for personalized agent memory",
            "content_type": "article",
            "days_ago": 1,
            "tags": ["readwise", "memory", "personalization"],
            "angles": ["memory", "highlights", "developer workflows"],
            "summary_seed": (
                "Provides a practical bridge between a user's reading backlog and downstream briefing generation."
            ),
        },
        {
            "title_template": "{topic}: highlight-aware summarization from reading history",
            "content_type": "highlight",
            "days_ago": 9,
            "tags": ["highlight", "knowledge", "agent tools"],
            "angles": ["highlight", "agent tools", "personal knowledge"],
            "summary_seed": (
                "Useful for turning previously saved material into structured signals"
                " instead of starting from raw web crawl."
            ),
        },
    ],
    "inoreader-intelligence-reports": [
        {
            "title_template": "{topic}: scheduled intelligence report benchmark",
            "content_type": "article",
            "days_ago": 3,
            "tags": ["reporting", "rss", "benchmark"],
            "angles": ["reporting", "rss", "analysis"],
            "summary_seed": (
                "A useful benchmark for briefing UX, scheduling, and report packaging even if it is not agent-first."
            ),
        },
        {
            "title_template": "{topic}: human-first digest design patterns",
            "content_type": "rss",
            "days_ago": 12,
            "tags": ["digest", "ux", "curation"],
            "angles": ["digest", "curation", "reader"],
            "summary_seed": (
                "Helps compare where current human-focused products stop"
                " and where agent-friendly pipelines should begin."
            ),
        },
    ],
}


def pick_summary(template: dict, summary_style: str, topic: str, source_name: str) -> str:
    seed = template["summary_seed"]
    if summary_style == "headline_only":
        return f"{topic}: {source_name} signal."
    if summary_style == "detailed":
        return (
            f"{seed} This prototype uses {source_name} as a source-layer stand-in to show "
            "how topic selection, preference matching, and explanation fields can work in "
            "a later real adapter."
        )
    return seed


class StaticSourceAdapter:
    """Simple source adapter backed by local templates."""

    def __init__(self, source: dict) -> None:
        self.source = source
        self.source_id: str = source["id"]

    def fetch(self, topic: str, summary_style: str, now: datetime | None = None) -> list[dict]:
        now = now or datetime.now(timezone.utc)
        source_url = self.source["url"].rstrip("/")
        candidates = []
        for template in SOURCE_ITEM_TEMPLATES.get(self.source["id"], []):
            item = deepcopy(template)
            published_at = now - timedelta(days=item["days_ago"])
            candidates.append(
                {
                    "id": f"{self.source['id']}-{topic.lower().replace(' ', '-')}-{item['content_type']}",
                    "title": item["title_template"].format(topic=topic),
                    "source": self.source["id"],
                    "source_name": self.source["name"],
                    "content_type": item["content_type"],
                    "url": f"{source_url}#news-report-{topic.lower().replace(' ', '-')}-{item['content_type']}",
                    "published_at": published_at,
                    "tags": item["tags"],
                    "angles": item["angles"],
                    "summary": pick_summary(item, summary_style, topic, self.source["name"]),
                    "source_meta": self.source,
                }
            )
        return candidates

    def ping(self) -> bool:
        """Mock adapter is always reachable."""
        return True
