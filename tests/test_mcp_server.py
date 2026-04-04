from __future__ import annotations

import json
import unittest

from news_report.mcp_server import (
    DEFAULT_MCP_BRIEFING_SOURCES,
    check_source_health_tool,
    generate_briefing_tool,
    list_sources_tool,
)


class MCPToolTests(unittest.TestCase):
    """Test MCP tool functions directly (no transport layer needed)."""

    def test_list_sources_returns_valid_json(self) -> None:
        result = list_sources_tool()
        sources = json.loads(result)
        self.assertIsInstance(sources, list)
        self.assertGreater(len(sources), 0)
        first = sources[0]
        for key in ("id", "name", "category", "interface_types", "agent_friendly"):
            self.assertIn(key, first, f"Missing key: {key}")

    def test_generate_briefing_json_output(self) -> None:
        result = generate_briefing_tool(
            topics=["AI"],
            sources=["podwise-cli", "readwise-cli"],
            max_items=3,
            output_format="json",
        )
        briefing = json.loads(result)
        self.assertIn("items", briefing)
        self.assertIn("coverage", briefing)
        self.assertLessEqual(len(briefing["items"]), 3)

    def test_generate_briefing_markdown_output(self) -> None:
        result = generate_briefing_tool(
            topics=["AI"],
            sources=["podwise-cli"],
            max_items=2,
            output_format="markdown",
        )
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# News Briefing"))

    def test_generate_briefing_defaults_curated_sources(self) -> None:
        result = generate_briefing_tool(topics=["AI"], max_items=2)
        briefing = json.loads(result)
        self.assertIn("coverage", briefing)
        self.assertEqual(briefing["coverage"]["matched_sources"], len(DEFAULT_MCP_BRIEFING_SOURCES))
        self.assertEqual(briefing["coverage"]["requested_sources"], len(DEFAULT_MCP_BRIEFING_SOURCES))

    def test_generate_briefing_invalid_output_format_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_format"):
            generate_briefing_tool(topics=["AI"], sources=["podwise-cli"], output_format="yaml")

    def test_check_source_health_all(self) -> None:
        result = check_source_health_tool()
        checks = json.loads(result)
        self.assertIsInstance(checks, list)
        self.assertGreater(len(checks), 0)
        first = checks[0]
        for key in ("source_id", "name", "adapter", "status"):
            self.assertIn(key, first, f"Missing key: {key}")

    def test_check_source_health_specific(self) -> None:
        result = check_source_health_tool(source_ids=["rsshub"])
        checks = json.loads(result)
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["source_id"], "rsshub")


class MCPResourceTests(unittest.TestCase):
    """Test MCP resource functions directly."""

    def test_sources_resource(self) -> None:
        from news_report.mcp_server import sources_resource

        result = sources_resource()
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_briefing_request_schema_resource(self) -> None:
        from news_report.mcp_server import briefing_request_schema_resource

        result = briefing_request_schema_resource()
        schema = json.loads(result)
        self.assertEqual(schema["type"], "object")
        self.assertIn("topics", schema["properties"])


if __name__ == "__main__":
    unittest.main()
