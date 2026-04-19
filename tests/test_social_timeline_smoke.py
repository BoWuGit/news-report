from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from social_timeline_runtime import cli


class SocialTimelineSmokeTests(unittest.TestCase):
    def test_scrape_and_normalize_smoke_with_three_items(self) -> None:
        fake_payload = {
            "site": "x",
            "page_url": "https://x.com/home",
            "items": [
                {"text": "post one about gpt", "url": "https://x.com/a/status/1"},
                {"text": "post two about agents", "url": "https://x.com/a/status/2"},
                {"text": "post three about mcp", "url": "https://x.com/a/status/3"},
                {"text": "post four should be truncated", "url": "https://x.com/a/status/4"},
            ],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            raw_path = Path(tmpdir) / "raw.json"
            normalized_path = Path(tmpdir) / "normalized.json"

            with patch("social_timeline_runtime.cli.scrape_site", return_value=fake_payload):
                code = cli.main(
                    [
                        "scrape",
                        "--site",
                        "x",
                        "--output",
                        str(raw_path),
                        "--max-items",
                        "3",
                    ]
                )
            self.assertEqual(code, 0)

            raw_payload = json.loads(raw_path.read_text(encoding="utf-8"))
            self.assertEqual(len(raw_payload["items"]), 3)
            self.assertEqual(raw_payload["items"][-1]["url"], "https://x.com/a/status/3")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "social_timeline_runtime.cli",
                    "normalize",
                    "--site",
                    "x",
                    "--input",
                    str(raw_path),
                    "--output",
                    str(normalized_path),
                    "--source-id",
                    "x-timeline",
                    "--source-name",
                    "X (Twitter)",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            normalized_payload = json.loads(normalized_path.read_text(encoding="utf-8"))
            self.assertEqual(len(normalized_payload), 3)


if __name__ == "__main__":
    unittest.main()
