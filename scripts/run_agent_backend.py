#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_SRC = ROOT / "packages" / "social_timeline_runtime" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from social_timeline_runtime.agent_backend import run_agent_task


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a task through a user-configured agent backend with a deterministic fallback."
    )
    parser.add_argument("--backend", choices=["auto", "codex", "claude", "fallback"], default="auto")
    parser.add_argument("--input", required=True, help="Path to a text prompt file.")
    parser.add_argument("--output", required=True, help="Path to write the backend result.")
    parser.add_argument("--fallback-text", default="Manual attention required.")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    code, message = run_agent_task(
        backend=args.backend,
        input_path=Path(args.input).resolve(),
        output_path=Path(args.output).resolve(),
        fallback_text=args.fallback_text,
        strict=args.strict,
    )
    stream = sys.stderr if message.startswith("error:") else sys.stdout
    print(message, file=stream)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
