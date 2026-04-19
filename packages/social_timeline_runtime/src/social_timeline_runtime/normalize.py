"""Normalization helpers for social timeline content.

This is the canonical home for extraction scripts and post normalization.
The ``news_report`` application re-exports from here for backward compatibility.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime

__all__ = [
    "JIKE_EXTRACTION_SCRIPT",
    "X_EXTRACTION_SCRIPT",
    "normalize_jike_posts",
    "normalize_x_posts",
]


# ---------------------------------------------------------------------------
# Stable ID generation
# ---------------------------------------------------------------------------


def _item_id(source_id: str, url: str = "", text: str = "") -> str:
    """Derive a stable unique ID, preferring URL over text for stability."""
    key = url if url else text[:200]
    return hashlib.sha256(f"{source_id}:{key}".encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Site-specific normalizers
# ---------------------------------------------------------------------------


def normalize_x_posts(raw_posts: list[dict], source_meta: dict, now: datetime) -> list[dict]:
    """Normalize raw X/Twitter post data into candidate dicts."""
    source_id = source_meta.get("id", "x-timeline")
    candidates = []
    for post in raw_posts:
        if post.get("is_ad"):
            continue
        text = post.get("text", "").strip()
        if not text:
            continue
        url = post.get("url", "")

        candidates.append(
            {
                "id": _item_id(source_id, url=url, text=text),
                "title": _make_title(text),
                "source": source_id,
                "source_name": source_meta.get("name", "X (Twitter)"),
                "content_type": "social_post",
                "url": url,
                "published_at": post.get("published_at", now),
                "tags": _extract_tags_from_text(text),
                "angles": ["social", "timeline"],
                "summary": text[:500],
                "source_meta": source_meta,
                "engagement": {
                    "likes": post.get("likes", 0),
                    "reposts": post.get("reposts", 0),
                    "replies": post.get("replies", 0),
                    "views": post.get("views", 0),
                },
                "author": post.get("author", ""),
                "author_handle": post.get("author_handle", ""),
                "quoted_post": post.get("quoted_post"),
            }
        )
    return candidates


def normalize_jike_posts(raw_posts: list[dict], source_meta: dict, now: datetime) -> list[dict]:
    """Normalize raw Jike post data into candidate dicts."""
    source_id = source_meta.get("id", "jike-following")
    candidates = []
    for post in raw_posts:
        text = post.get("text", "").strip()
        if not text:
            continue
        url = post.get("url", "")

        candidates.append(
            {
                "id": _item_id(source_id, url=url, text=text),
                "title": _make_title(text),
                "source": source_id,
                "source_name": source_meta.get("name", "即刻"),
                "content_type": "social_post",
                "url": url,
                "published_at": post.get("published_at", now),
                "tags": _extract_tags_from_text(text),
                "angles": ["social", "timeline"],
                "summary": text[:500],
                "source_meta": source_meta,
                "engagement": {
                    "likes": post.get("likes", 0),
                    "reposts": post.get("reposts", 0),
                    "comments": post.get("comments", 0),
                },
                "author": post.get("author", ""),
                "topic": post.get("topic", ""),
            }
        )
    return candidates


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_title(text: str, max_len: int = 80) -> str:
    """Create a short title from post text."""
    first_line = text.split("\n")[0].strip()
    if len(first_line) <= max_len:
        return first_line
    return first_line[: max_len - 1] + "…"


def _extract_tags_from_text(text: str) -> list[str]:
    """Extract hashtags and keywords from social post text."""
    tags = []
    lower = text.lower()
    for match in re.finditer(r"#(\w+)", text):
        tags.append(match.group(1).lower())

    topic_keywords = {
        "ai": [r"\bai\b", r"\bllm\b", r"\bgpt\b", r"\bclaude\b", r"\bagent\b", "模型", "人工智能"],
        "open source": [r"\bopen source\b", "开源", r"\bgithub\b"],
        "startup": [r"\bstartup\b", "创业", r"\bfounder\b", r"\bco-founder\b"],
        "dev tools": [r"\bdeveloper\b", r"\bcoding\b", "编程", r"\bmcp\b"],
    }
    for topic, patterns in topic_keywords.items():
        if any(re.search(p, lower) for p in patterns):
            tags.append(topic)

    return tags if tags else ["general"]


# ---------------------------------------------------------------------------
# CDP extraction scripts (executed inside browser context)
# ---------------------------------------------------------------------------

X_EXTRACTION_SCRIPT = """
() => {
    const articles = document.querySelectorAll('article');
    const posts = [];
    for (const article of articles) {
        const text = article.innerText || '';
        const isAd = text.includes('广告') || text.includes('Promoted');
        const links = article.querySelectorAll('a[href*="/status/"]');
        const statusLink = links.length > 0 ? links[links.length - 1].href : '';

        // Extract engagement metrics from button text
        const buttons = article.querySelectorAll('button');
        let likes = 0, reposts = 0, replies = 0, views = 0;
        for (const btn of buttons) {
            const label = btn.getAttribute('aria-label') || '';
            const likeMatch = label.match(/(\\d+)\\s*(喜欢|Like)/i);
            const repostMatch = label.match(/(\\d+)\\s*(转帖|Repost)/i);
            const replyMatch = label.match(/(\\d+)\\s*(回复|Repl)/i);
            if (likeMatch) likes = parseInt(likeMatch[1]);
            if (repostMatch) reposts = parseInt(repostMatch[1]);
            if (replyMatch) replies = parseInt(replyMatch[1]);
        }

        // Extract author
        const authorLink = article.querySelector('a[href^="/"][role="link"]');
        const authorHandle = authorLink ? authorLink.getAttribute('href').replace('/', '@') : '';

        posts.push({
            text: text.substring(0, 1000),
            url: statusLink,
            is_ad: isAd,
            likes, reposts, replies,
            author_handle: authorHandle,
        });
    }
    return posts;
}
"""

JIKE_EXTRACTION_SCRIPT = """
() => {
    const posts = document.querySelectorAll("[class*=_post_]");
    const items = [];
    for (const post of posts) {
        const authorEl = post.querySelector("[class*=_root_1o1bm]")
                      || post.querySelector("a[href*='/u/']");
        const author = authorEl?.innerText?.trim() || "";

        const header = post.querySelector("header");
        const headerText = header?.innerText || "";
        const timeMatch = headerText.match(
            /(\\d+\\s*[分秒时天周月年].*?前|\\d+\\s*(min|hour|day|week)s?\\s*ago|just now|刚刚)/i
        );
        const timeText = timeMatch ? timeMatch[0] : "";

        const contentEl = post.querySelector("[class*=_content_]");
        const rawText = contentEl?.innerText || post.innerText || "";
        // Strip author name and time prefix from content
        const text = rawText.replace(new RegExp("^" + author.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&") + "\\n?"), "")
                           .replace(/^(\\d+[分秒时天周月年].*?前|刚刚)\\n?/, "")
                           .replace(/\\n\\d+\\n\\d+\\n\\d+$/, "")
                           .trim();

        const topicLink = post.querySelector("a[href*='/topic/']");
        const topic = topicLink?.innerText?.trim() || "";

        if (!text || text.length < 5) continue;
        items.push({ author, timeText, topic, text: text.substring(0, 500) });
    }
    return items;
}
"""
