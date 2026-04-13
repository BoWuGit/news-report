#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

BACKEND_ENVS = {
    "codex": "CODEX_AGENT_CMD",
    "claude": "CLAUDE_AGENT_CMD",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a task through a user-configured agent backend with a deterministic fallback."
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "codex", "claude", "fallback"],
        default="auto",
        help="Backend to use. 'auto' picks the first configured backend.",
    )
    parser.add_argument("--input", required=True, help="Path to a text prompt file.")
    parser.add_argument("--output", required=True, help="Path to write the backend result.")
    parser.add_argument(
        "--fallback-text",
        default="Manual attention required.",
        help="Deterministic text written when no backend is available or invocation fails.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero instead of falling back if the selected backend cannot be used.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def configured_backends() -> list[str]:
    return [backend for backend, env_name in BACKEND_ENVS.items() if os.environ.get(env_name, "").strip()]


def resolve_backend(requested: str) -> str:
    if requested != "auto":
        return requested
    available = configured_backends()
    return available[0] if available else "fallback"


def run_external_backend(backend: str, prompt: str) -> subprocess.CompletedProcess[str]:
    env_name = BACKEND_ENVS[backend]
    command = os.environ.get(env_name, "").strip()
    if not command:
        raise RuntimeError(
            f"{backend} backend is not configured. Set {env_name} to a command that accepts stdin and writes stdout."
        )

    return subprocess.run(
        shlex.split(command),
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    prompt = read_text(input_path)

    backend = resolve_backend(args.backend)
    if backend == "fallback":
        write_text(output_path, args.fallback_text)
        print("backend=fallback")
        return 0

    try:
        completed = run_external_backend(backend, prompt)
    except Exception as exc:
        if args.strict:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        write_text(output_path, args.fallback_text)
        print(f"backend=fallback reason={exc}")
        return 0

    if completed.returncode != 0:
        if args.strict:
            stderr = completed.stderr.strip() or "backend invocation failed"
            print(f"error: {stderr}", file=sys.stderr)
            return completed.returncode
        write_text(output_path, args.fallback_text)
        print(f"backend=fallback reason=command-exited-{completed.returncode}")
        return 0

    write_text(output_path, completed.stdout)
    print(f"backend={backend}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
