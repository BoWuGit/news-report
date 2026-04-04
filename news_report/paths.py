"""Resolve repo-root vs wheel-bundled data and schema directories."""

from __future__ import annotations

from pathlib import Path


def resolve_package_adjacent_dir(name: str) -> Path:
    """Resolve *name* (e.g. ``data``, ``schemas``): repo root first, else under package."""
    pkg = Path(__file__).resolve().parent
    repo = pkg.parent / name
    if repo.is_dir():
        return repo
    return pkg / name
