"""Tests for the Markdown formatter."""

from __future__ import annotations

import unittest

from news_report.formatter import format_briefing_markdown


class FormatterTests(unittest.TestCase):
    def test_empty_items(self) -> None:
        briefing = {"generated_at": "2026-03-31T00:00:00Z", "items": [], "coverage": {}}
        result = format_briefing_markdown(briefing)
        self.assertIn("No items matched", result)

    def test_normal_output_contains_title(self) -> None:
        briefing = {
            "generated_at": "2026-03-31T00:00:00Z",
            "items": [
                {
                    "title": "Test Article",
                    "url": "https://example.com",
                    "source": "test",
                    "content_type": "article",
                    "score": 0.85,
                    "why_it_matters": "Strong match",
                    "summary": "A test summary.",
                }
            ],
            "coverage": {
                "requested_sources": 1,
                "matched_sources": 1,
                "generated_candidates": 5,
                "returned_items": 1,
            },
        }
        result = format_briefing_markdown(briefing)
        self.assertIn("[Test Article](https://example.com)", result)
        self.assertIn("0.85", result)
        self.assertIn("Strong match", result)

    def test_item_without_url(self) -> None:
        briefing = {
            "generated_at": "2026-03-31T00:00:00Z",
            "items": [
                {
                    "title": "No URL",
                    "url": "",
                    "source": "test",
                    "content_type": "article",
                    "score": 0.5,
                    "why_it_matters": "",
                    "summary": "",
                }
            ],
            "coverage": {},
        }
        result = format_briefing_markdown(briefing)
        self.assertIn("## 1. No URL", result)
        self.assertNotIn("[No URL]", result)


if __name__ == "__main__":
    unittest.main()
