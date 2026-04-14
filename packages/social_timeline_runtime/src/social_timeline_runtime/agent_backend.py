"""Agent backend runner for the social timeline runtime.

This is copied from the existing script-based implementation so the runtime can
own a stable Python API and CLI entry point. The old script should become a thin
wrapper over this module until it can be removed.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

BACKEND_ENVS = {
    "codex": "CODEX_AGENT_CMD",
    "claude": "CLAUDE_AGENT_CMD",
}


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


def run_agent_task(
    backend: str,
    input_path: Path,
    output_path: Path,
    fallback_text: str = "Manual attention required.",
    strict: bool = False,
) -> tuple[int, str]:
    prompt = read_text(input_path)
    selected = resolve_backend(backend)

    if selected == "fallback":
        write_text(output_path, fallback_text)
        return 0, "backend=fallback"

    try:
        completed = run_external_backend(selected, prompt)
    except Exception as exc:
        if strict:
            return 1, f"error: {exc}"
        write_text(output_path, fallback_text)
        return 0, f"backend=fallback reason={exc}"

    if completed.returncode != 0:
        if strict:
            stderr = completed.stderr.strip() or "backend invocation failed"
            return completed.returncode, f"error: {stderr}"
        write_text(output_path, fallback_text)
        return 0, f"backend=fallback reason=command-exited-{completed.returncode}"

    write_text(output_path, completed.stdout)
    return 0, f"backend={selected}"
