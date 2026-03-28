#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "docs" / "catalog.md"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from news_report.catalog import load_sources, validate_sources


def render_catalog(sources: list[dict]) -> str:
    lines = [
        "# Resource Catalog",
        "",
        "This file is generated from `data/sources.json` by `scripts/build_catalog.py`.",
        "",
    ]

    by_category: dict[str, list[dict]] = {}
    for source in sources:
        by_category.setdefault(source["category"], []).append(source)

    for category in sorted(by_category):
        lines.append(f"## {category}")
        lines.append("")

        for source in sorted(by_category[category], key=lambda item: item["name"].lower()):
            open_source = "yes" if source["open_source"] else "no"
            interfaces = ", ".join(f"`{value}`" for value in source["interface_types"])
            content_types = ", ".join(f"`{value}`" for value in source["content_types"])

            lines.extend(
                [
                    f"### {source['name']}",
                    "",
                    f"- id: `{source['id']}`",
                    f"- url: {source['url']}",
                    f"- interfaces: {interfaces}",
                    f"- content types: {content_types}",
                    f"- open source: `{open_source}`",
                    f"- agent friendly: `{source['agent_friendly']}`",
                    f"- pricing: `{source['pricing']}`",
                    f"- stage: `{source['stage']}`",
                    f"- summary: {source['summary']}",
                ]
            )

            for note in source.get("notes", []):
                lines.append(f"- note: {note}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    sources = validate_sources(load_sources())
    rendered = render_catalog(sources)
    CATALOG_PATH.write_text(rendered, encoding="utf-8")
    print(f"validated {len(sources)} sources")
    print(f"wrote {CATALOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
