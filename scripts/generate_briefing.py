#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from news_report.briefing import generate_briefing, validate_request
from news_report.catalog import load_json, load_sources, validate_sources


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 scripts/generate_briefing.py <request.json>", file=sys.stderr)
        return 1

    request_path = Path(sys.argv[1]).resolve()
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


if __name__ == "__main__":
    raise SystemExit(main())
