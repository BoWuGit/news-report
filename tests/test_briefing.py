from __future__ import annotations

import unittest

from news_report.briefing import generate_briefing, validate_request
from news_report.catalog import load_sources, validate_sources


class BriefingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = validate_sources(load_sources())
        self.request = validate_request(
            {
                "topics": ["AI", "open source"],
                "sources": [
                    "podwise-cli",
                    "readwise-cli",
                    "inoreader-intelligence-reports",
                ],
                "language": "zh-CN",
                "max_items": 5,
                "summary_style": "concise",
                "user_profile": {
                    "explicit_preferences": [
                        "agent tools",
                        "developer workflows",
                        "local first",
                    ],
                    "blocked_topics": ["crypto trading"],
                    "time_decay_days": 30,
                    "diversity_floor": 0.2,
                },
            }
        )

    def test_generate_briefing_returns_requested_shape(self) -> None:
        briefing = generate_briefing(self.request, self.sources)
        self.assertEqual(briefing["coverage"]["requested_sources"], 3)
        self.assertEqual(briefing["coverage"]["matched_sources"], 3)
        self.assertLessEqual(len(briefing["items"]), self.request["max_items"])
        self.assertTrue(all("score_breakdown" in item for item in briefing["items"]))

    def test_diversity_rerank_spreads_top_results(self) -> None:
        briefing = generate_briefing(self.request, self.sources)
        top_sources = {item["source"] for item in briefing["items"][:3]}
        self.assertEqual(len(top_sources), 3)

    def test_unknown_sources_raise(self) -> None:
        bad_request = dict(self.request)
        bad_request["sources"] = ["unknown-source"]
        with self.assertRaisesRegex(ValueError, "No requested sources matched"):
            generate_briefing(bad_request, self.sources)

    def test_blocked_topics_filter_matching_candidates(self) -> None:
        blocked_request = dict(self.request)
        blocked_request["user_profile"] = dict(self.request["user_profile"])
        blocked_request["user_profile"]["blocked_topics"] = ["agent tools"]
        briefing = generate_briefing(blocked_request, self.sources)
        blocked_ids = {item["id"] for item in briefing["items"]}
        self.assertNotIn("podwise-cli-ai-podcast", blocked_ids)

    def test_blocked_topics_do_not_filter_requested_topics_by_name(self) -> None:
        blocked_request = dict(self.request)
        blocked_request["topics"] = ["AI"]
        blocked_request["sources"] = ["podwise-cli", "readwise-cli"]
        blocked_request["user_profile"] = dict(self.request["user_profile"])
        blocked_request["user_profile"]["blocked_topics"] = ["AI"]
        briefing = generate_briefing(blocked_request, self.sources)
        self.assertGreater(briefing["coverage"]["generated_candidates"], 0)
        self.assertGreater(len(briefing["items"]), 0)


if __name__ == "__main__":
    unittest.main()
