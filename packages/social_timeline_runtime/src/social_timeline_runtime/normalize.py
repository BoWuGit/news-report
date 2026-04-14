"""Normalization helpers for social timeline content.

During migration this module bridges to the existing `news_report` implementation
so callers can adopt the runtime contract first. Once extraction is complete, the
logic should live here permanently and `news_report` should consume this package.
"""

from __future__ import annotations

from news_report.adapters.cdp_browser import (
    JIKE_EXTRACTION_SCRIPT,
    X_EXTRACTION_SCRIPT,
    normalize_jike_posts,
    normalize_x_posts,
)

__all__ = [
    "JIKE_EXTRACTION_SCRIPT",
    "X_EXTRACTION_SCRIPT",
    "normalize_jike_posts",
    "normalize_x_posts",
]
