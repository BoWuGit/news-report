from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from news_report.adapters import build_adapter_registry
from news_report.briefing import generate_briefing, validate_request
from news_report.catalog import load_json, load_sources, validate_sources
from news_report.formatter import format_briefing_markdown
from scripts.build_catalog import render_catalog


def build_catalog_cli() -> int:
    sources = validate_sources(load_sources())

    root = Path(__file__).resolve().parent.parent
    catalog_path = root / "docs" / "catalog.md"

    rendered = render_catalog(sources)
    catalog_path.write_text(rendered, encoding="utf-8")
    print(f"validated {len(sources)} sources")
    print(f"wrote {catalog_path.relative_to(root)}")
    return 0


def _check_sources_cli() -> int:
    """Ping every source adapter and report health."""

    sources = validate_sources(load_sources())
    registry = build_adapter_registry(sources)
    all_ok = True
    for source in sources:
        sid = source["id"]
        adapter = registry[sid]
        ok = adapter.ping()
        status = "OK" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  {status}  {sid} ({type(adapter).__name__})")
    return 0 if all_ok else 1


def generate_briefing_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="generate-briefing", description="Generate a news briefing.")
    parser.add_argument("request_json", nargs="?", help="Path to the briefing request JSON file")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", dest="output_format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    parser.add_argument("--check-sources", action="store_true", help="Ping sources and exit")

    args = parser.parse_args(argv or sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    if args.check_sources:
        return _check_sources_cli()

    if not args.request_json:
        parser.error("request_json is required unless --check-sources is used")

    request_path = Path(args.request_json).resolve()
    try:
        request = validate_request(load_json(request_path))
        sources = validate_sources(load_sources())
        briefing = generate_briefing(request, sources)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output_format == "markdown":
        sys.stdout.write(format_briefing_markdown(briefing))
    else:
        json.dump(briefing, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0
