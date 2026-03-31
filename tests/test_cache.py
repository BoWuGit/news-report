"""Tests for the briefing cache module."""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from news_report.cache import cache_key, cache_read, cache_write


class CacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        os.environ["NEWS_REPORT_CACHE_DIR"] = self.tmpdir
        os.environ["NEWS_REPORT_CACHE_TTL"] = "60"
        # Force reload of module-level CACHE_DIR
        import news_report.cache as mod

        mod.CACHE_DIR = __import__("pathlib").Path(self.tmpdir)

    def tearDown(self) -> None:
        os.environ.pop("NEWS_REPORT_CACHE_DIR", None)
        os.environ.pop("NEWS_REPORT_CACHE_TTL", None)

    def test_cache_roundtrip(self) -> None:
        request = {"topics": ["AI"], "sources": ["rsshub"]}
        key = cache_key(request)
        briefing = {"items": [{"id": "1"}], "generated_at": "2026-03-31T00:00:00Z"}
        cache_write(key, briefing)
        result = cache_read(key)
        self.assertIsNotNone(result)
        self.assertEqual(result["items"], briefing["items"])

    def test_cache_miss_returns_none(self) -> None:
        self.assertIsNone(cache_read("nonexistent-key"))

    def test_cache_expired_returns_none(self) -> None:
        import time

        import news_report.cache as mod

        request = {"topics": ["test"]}
        key = cache_key(request)
        # Write with a timestamp in the past
        payload = {"items": [], "_cached_at": time.time() - 9999}
        path = mod.CACHE_DIR / f"{key}.json"
        mod.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.assertIsNone(cache_read(key))

    def test_corrupt_cache_returns_none(self) -> None:
        import news_report.cache as mod

        key = "corrupt-key"
        path = mod.CACHE_DIR / f"{key}.json"
        mod.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text("NOT VALID JSON {{{{", encoding="utf-8")
        self.assertIsNone(cache_read(key))
        # File should be cleaned up
        self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
