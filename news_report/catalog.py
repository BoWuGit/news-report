from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "data" / "sources.json"

REQUIRED_SOURCE_FIELDS = {
    "id",
    "name",
    "url",
    "category",
    "interface_types",
    "content_types",
    "open_source",
    "agent_friendly",
    "stage",
    "pricing",
    "summary",
    "last_verified",
}


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_sources(path: Path = SOURCES_PATH) -> list[dict]:
    sources = load_json(path)
    if not isinstance(sources, list):
        raise ValueError("data/sources.json must contain a top-level array")
    return sources


def validate_sources(sources: list[dict]) -> list[dict]:
    ids = set()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError(f"Entry {index} must be an object")

        missing = REQUIRED_SOURCE_FIELDS - set(source.keys())
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise ValueError(f"Entry {index} is missing fields: {missing_fields}")

        source_id = source["id"]
        if source_id in ids:
            raise ValueError(f"Duplicate source id: {source_id}")
        ids.add(source_id)

        if not isinstance(source["interface_types"], list) or not source["interface_types"]:
            raise ValueError(f"{source_id}: interface_types must be a non-empty array")

        if not isinstance(source["content_types"], list) or not source["content_types"]:
            raise ValueError(f"{source_id}: content_types must be a non-empty array")

    return sources
