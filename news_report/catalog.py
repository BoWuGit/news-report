from __future__ import annotations

import json
from pathlib import Path

import jsonschema

_ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = _ROOT / "data" / "sources.json"
SCHEMAS_DIR = _ROOT / "schemas"


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_schema(name: str) -> dict:
    path = SCHEMAS_DIR / name
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_sources(path: Path = SOURCES_PATH) -> list[dict]:
    sources = load_json(path)
    if not isinstance(sources, list):
        raise ValueError("data/sources.json must contain a top-level array")
    return sources


def validate_sources(sources: list[dict]) -> list[dict]:
    """Validate every source entry against the JSON Schema."""
    schema = _load_schema("source.schema.json")
    ids: set[str] = set()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError(f"Entry {index} must be an object")
        try:
            jsonschema.validate(instance=source, schema=schema)
        except jsonschema.ValidationError as exc:
            raise ValueError(f"Entry {index} ({source.get('id', '?')}): {exc.message}") from exc

        source_id = source["id"]
        if source_id in ids:
            raise ValueError(f"Duplicate source id: {source_id}")
        ids.add(source_id)

    return sources
