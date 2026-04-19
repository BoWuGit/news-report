from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_SRC = ROOT / "packages" / "social_timeline_runtime" / "src"

import sys  # noqa: E402

if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from social_timeline_runtime.sites import _detect_jike_login, _detect_x_login  # noqa: E402


class LoginDetectionTests(unittest.TestCase):
    def test_detect_x_logged_in_when_articles_visible(self) -> None:
        status = _detect_x_login(
            {
                "url": "https://x.com/home",
                "title": "Home / X",
                "body": "timeline body",
                "articleCount": 3,
            }
        )
        self.assertTrue(status.logged_in)
        self.assertEqual(status.reason, "timeline_visible")

    def test_detect_x_login_prompt(self) -> None:
        status = _detect_x_login(
            {
                "url": "https://x.com/i/flow/login",
                "title": "Login on X",
                "body": "Sign in to continue",
                "articleCount": 0,
            }
        )
        self.assertFalse(status.logged_in)
        self.assertEqual(status.reason, "login_prompt")

    def test_detect_jike_logged_in_when_viewport_has_text(self) -> None:
        status = _detect_jike_login(
            {
                "url": "https://web.okjike.com/following",
                "title": "即刻",
                "body": "",
                "viewportText": "朋友更新内容",
            }
        )
        self.assertTrue(status.logged_in)
        self.assertEqual(status.reason, "timeline_visible")


class RuntimeCliNormalizationTests(unittest.TestCase):
    def test_normalize_command_writes_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "raw.json"
            output_path = Path(tmpdir) / "candidates.json"
            input_path.write_text(
                json.dumps({"items": [{"text": "GPT agents are getting better", "url": "https://x.com/a/status/1"}]}),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    "python3",
                    "-m",
                    "social_timeline_runtime.cli",
                    "normalize",
                    "--site",
                    "x",
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--source-id",
                    "x-timeline",
                    "--source-name",
                    "X (Twitter)",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": str(RUNTIME_SRC)},
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload), 1)
            self.assertEqual(payload[0]["source"], "x-timeline")


if __name__ == "__main__":
    unittest.main()
