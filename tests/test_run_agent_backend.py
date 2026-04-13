from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "run_agent_backend.py"


class RunAgentBackendTests(unittest.TestCase):
    def test_fallback_when_no_backend_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "prompt.txt"
            output_path = Path(tmpdir) / "result.txt"
            input_path.write_text("Prompt body", encoding="utf-8")

            env = os.environ.copy()
            env.pop("CODEX_AGENT_CMD", None)
            env.pop("CLAUDE_AGENT_CMD", None)

            completed = subprocess.run(
                ["python3", str(SCRIPT), "--backend", "auto", "--input", str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
                env=env,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertIn("backend=fallback", completed.stdout)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "Manual attention required.")

    def test_external_backend_uses_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "prompt.txt"
            output_path = Path(tmpdir) / "result.txt"
            input_path.write_text("hello backend", encoding="utf-8")

            env = os.environ.copy()
            env["CODEX_AGENT_CMD"] = 'python3 -c "import sys; print(sys.stdin.read().upper())"'

            completed = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--backend",
                    "codex",
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
                env=env,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertIn("backend=codex", completed.stdout)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "HELLO BACKEND\n")

    def test_strict_mode_fails_without_backend_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "prompt.txt"
            output_path = Path(tmpdir) / "result.txt"
            input_path.write_text("Prompt body", encoding="utf-8")

            env = os.environ.copy()
            env.pop("CODEX_AGENT_CMD", None)

            completed = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--backend",
                    "codex",
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--strict",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
                env=env,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("not configured", completed.stderr)
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
