"""Tests for the adapter package: Protocol, registry, mock, and RSSHub."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from news_report.adapters import SourceAdapter, build_adapter_registry
from news_report.adapters.mock import StaticSourceAdapter
from news_report.adapters.rsshub import RSSHubAdapter, _parse_published
from news_report.catalog import load_sources, validate_sources


class ProtocolConformanceTests(unittest.TestCase):
    """Ensure adapters satisfy the SourceAdapter Protocol."""

    def _make_source(self, sid: str = "test") -> dict:
        return {
            "id": sid,
            "name": "Test",
            "url": "https://example.com",
            "category": "open_source_project",
            "interface_types": ["rss"],
            "content_types": ["article"],
            "open_source": True,
            "agent_friendly": "high",
            "stage": "active",
            "pricing": "free",
            "summary": "Test source.",
            "last_verified": "2026-03-30",
        }

    def test_static_adapter_is_source_adapter(self) -> None:
        adapter = StaticSourceAdapter(self._make_source())
        self.assertIsInstance(adapter, SourceAdapter)

    def test_rsshub_adapter_is_source_adapter(self) -> None:
        adapter = RSSHubAdapter(self._make_source("rsshub"))
        self.assertIsInstance(adapter, SourceAdapter)

    def test_static_adapter_ping_returns_true(self) -> None:
        adapter = StaticSourceAdapter(self._make_source())
        self.assertTrue(adapter.ping())


class RegistryTests(unittest.TestCase):
    """Tests for build_adapter_registry()."""

    def test_rsshub_source_gets_real_adapter(self) -> None:
        sources = validate_sources(load_sources())
        registry = build_adapter_registry(sources)
        self.assertIsInstance(registry["rsshub"], RSSHubAdapter)

    def test_non_rsshub_source_gets_mock(self) -> None:
        sources = validate_sources(load_sources())
        registry = build_adapter_registry(sources)
        self.assertIsInstance(registry["podwise-cli"], StaticSourceAdapter)


class RSSHubAdapterTests(unittest.TestCase):
    """Tests for RSSHubAdapter with mocked HTTP."""

    def setUp(self) -> None:
        self.source = {
            "id": "rsshub",
            "name": "RSSHub",
            "url": "https://github.com/DIYgod/RSSHub",
            "category": "open_source_project",
            "interface_types": ["rss", "web"],
            "content_types": ["rss", "article", "feed"],
            "open_source": True,
            "agent_friendly": "high",
            "stage": "active",
            "pricing": "free",
            "summary": "RSS feed generation.",
            "last_verified": "2026-03-30",
        }
        self.adapter = RSSHubAdapter(self.source)

    @patch.object(RSSHubAdapter, "_fetch_route")
    def test_fetch_returns_candidates(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = [{"id": "1", "title": "Test"}]
        results = self.adapter.fetch("AI", "concise")
        # "AI" maps to 2 routes, each returning 1 item
        self.assertGreaterEqual(len(results), 1)
        mock_fetch.assert_called()

    @patch.object(RSSHubAdapter, "_fetch_route", side_effect=Exception("timeout"))
    def test_fetch_returns_empty_on_failure(self, mock_fetch: MagicMock) -> None:
        results = self.adapter.fetch("AI", "concise")
        self.assertEqual(results, [])

    def test_fetch_caps_at_50(self) -> None:
        items = [{"id": str(i), "title": f"Item {i}"} for i in range(60)]
        with patch.object(self.adapter, "_fetch_route", return_value=items):
            results = self.adapter.fetch("AI", "concise")
        self.assertLessEqual(len(results), 50)

    @patch("news_report.adapters.rsshub.httpx.Client.get")
    def test_ping_returns_true_on_success(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=200)
        self.assertTrue(self.adapter.ping())

    @patch("news_report.adapters.rsshub.httpx.Client.get", side_effect=Exception("connection refused"))
    def test_ping_returns_false_on_error(self, mock_get: MagicMock) -> None:
        self.assertFalse(self.adapter.ping())


class ParsePublishedTests(unittest.TestCase):
    def test_none_published_parsed_falls_back(self) -> None:
        entry = {"published_parsed": None}
        result = _parse_published(entry)
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.tzinfo, UTC)

    def test_valid_published_parsed(self) -> None:
        from time import struct_time

        # 2026-01-15 12:00:00 UTC as struct_time
        st = struct_time((2026, 1, 15, 12, 0, 0, 2, 15, 0))
        entry = {"published_parsed": st}
        result = _parse_published(entry)
        self.assertEqual(result.year, 2026)


if __name__ == "__main__":
    unittest.main()
