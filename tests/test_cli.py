from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from news_report.cli import generate_briefing_cli, main

ROOT = Path(__file__).resolve().parent.parent


class CLITests(unittest.TestCase):
    def _run_main(self, argv: list[str], stdin_text: str | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        stdin = io.StringIO(stdin_text or "")
        with patch("sys.stdin", stdin), redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_generate_briefing_legacy_cli_reads_stdin(self) -> None:
        request = (ROOT / "examples" / "briefing-request.json").read_text(encoding="utf-8")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch("sys.stdin", io.StringIO(request)), redirect_stdout(stdout), redirect_stderr(stderr):
            code = generate_briefing_cli(["-", "--format", "json"])

        self.assertEqual(code, 0, stderr.getvalue())
        briefing = json.loads(stdout.getvalue())
        self.assertIn("items", briefing)
        self.assertIn("coverage", briefing)

    def test_unified_briefing_generate_reads_stdin(self) -> None:
        request = (ROOT / "examples" / "briefing-request.json").read_text(encoding="utf-8")
        code, stdout, stderr = self._run_main(["briefing", "generate", "-"], stdin_text=request)
        self.assertEqual(code, 0, stderr)
        self.assertIn("items", json.loads(stdout))

    def test_sources_list_json(self) -> None:
        code, stdout, stderr = self._run_main(["sources", "list", "--json"])
        self.assertEqual(code, 0, stderr)
        sources = json.loads(stdout)
        self.assertIsInstance(sources, list)
        self.assertTrue(any(source["id"] == "rsshub" for source in sources))

    def test_sources_get_json(self) -> None:
        code, stdout, stderr = self._run_main(["sources", "get", "podwise-cli", "--json"])
        self.assertEqual(code, 0, stderr)
        source = json.loads(stdout)
        self.assertEqual(source["id"], "podwise-cli")

    def test_sources_check_json_for_mock_source(self) -> None:
        code, stdout, stderr = self._run_main(["sources", "check", "podwise-cli", "--json"])
        self.assertEqual(code, 0, stderr)
        checks = json.loads(stdout)
        self.assertEqual(checks[0]["source_id"], "podwise-cli")
        self.assertEqual(checks[0]["status"], "ok")

    def test_schemas_list_and_get(self) -> None:
        code, stdout, stderr = self._run_main(["schemas", "list", "--json"])
        self.assertEqual(code, 0, stderr)
        schemas = json.loads(stdout)
        self.assertTrue(any(schema["name"] == "briefing-request" for schema in schemas))

        code, stdout, stderr = self._run_main(["schemas", "get", "briefing-request"])
        self.assertEqual(code, 0, stderr)
        schema = json.loads(stdout)
        self.assertEqual(schema["title"], "Briefing Request")

    def test_doctor_json_skip_network(self) -> None:
        code, stdout, stderr = self._run_main(["doctor", "--json", "--skip-network"])
        self.assertEqual(code, 0, stderr)
        result = json.loads(stdout)
        self.assertIn("checks", result)
        self.assertEqual(result["summary"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
