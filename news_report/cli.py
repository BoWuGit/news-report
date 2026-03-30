from __future__ import annotations

import json
import sys
from pathlib import Path

from news_report.briefing import generate_briefing, validate_request
from news_report.catalog import load_json, load_sources, validate_sources


def build_catalog_cli() -> int:
    from scripts.build_catalog import main as build_catalog_main

    build_catalog_main()
    return 0


def generate_briefing_cli(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print("usage: generate-briefing <request.json>", file=sys.stderr)
        return 1

    request_path = Path(argv[0]).resolve()
    try:
        request = validate_request(load_json(request_path))
        sources = validate_sources(load_sources())
        briefing = generate_briefing(request, sources)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(briefing, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0
