"""Tests for JSON Schema validation in briefing.py and catalog.py."""

from __future__ import annotations

import unittest

from news_report.briefing import validate_briefing_response, validate_request
from news_report.catalog import load_sources, validate_sources


class RequestSchemaTests(unittest.TestCase):
    def _valid_request(self) -> dict:
        return {
            "topics": ["AI"],
            "sources": ["rsshub"],
            "language": "en",
            "max_items": 5,
            "summary_style": "concise",
            "user_profile": {
                "explicit_preferences": ["agent tools"],
                "blocked_topics": [],
                "time_decay_days": 30,
                "diversity_floor": 0.2,
            },
        }

    def test_valid_request_passes(self) -> None:
        result = validate_request(self._valid_request())
        self.assertEqual(result["topics"], ["AI"])

    def test_missing_field_raises(self) -> None:
        req = self._valid_request()
        del req["topics"]
        with self.assertRaises(ValueError):
            validate_request(req)

    def test_invalid_max_items_raises(self) -> None:
        req = self._valid_request()
        req["max_items"] = 0
        with self.assertRaises(ValueError):
            validate_request(req)

    def test_invalid_summary_style_raises(self) -> None:
        req = self._valid_request()
        req["summary_style"] = "ultra"
        with self.assertRaises(ValueError):
            validate_request(req)

    def test_non_dict_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate_request([1, 2, 3])


class BriefingResponseSchemaTests(unittest.TestCase):
    def test_minimal_valid_briefing_passes(self) -> None:
        briefing = {
            "generated_at": "2026-01-01T00:00:00Z",
            "query": {
                "topics": ["AI"],
                "sources": ["podwise-cli"],
                "language": "en",
                "max_items": 5,
                "summary_style": "concise",
            },
            "items": [
                {
                    "id": "x",
                    "title": "T",
                    "source": "podwise-cli",
                    "content_type": "article",
                    "url": "https://example.com/",
                    "published_at": "2026-01-01T00:00:00Z",
                    "summary": "S",
                    "why_it_matters": "W",
                    "score": 0.5,
                    "score_breakdown": {
                        "source_quality": 0.1,
                        "topic_match": 0.2,
                        "preference_match": 0.3,
                        "freshness": 0.4,
                        "diversity": 0.5,
                    },
                    "tags": ["a"],
                }
            ],
            "coverage": {
                "requested_sources": 1,
                "matched_sources": 1,
                "generated_candidates": 1,
                "returned_items": 1,
            },
        }
        validate_briefing_response(briefing)


class SourceSchemaTests(unittest.TestCase):
    def test_real_sources_validate(self) -> None:
        sources = load_sources()
        result = validate_sources(sources)
        self.assertGreaterEqual(len(result), 15)

    def test_invalid_source_raises(self) -> None:
        bad = [{"id": "test"}]  # Missing most fields
        with self.assertRaises(ValueError):
            validate_sources(bad)

    def test_duplicate_id_raises(self) -> None:
        source = {
            "id": "dup",
            "name": "Dup",
            "url": "https://example.com",
            "category": "open_source_project",
            "interface_types": ["rss"],
            "content_types": ["article"],
            "open_source": True,
            "agent_friendly": "high",
            "stage": "active",
            "pricing": "free",
            "summary": "Test.",
            "last_verified": "2026-03-30",
        }
        with self.assertRaises(ValueError):
            validate_sources([source, source])


if __name__ == "__main__":
    unittest.main()
