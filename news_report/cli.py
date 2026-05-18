from __future__ import annotations

import argparse
import importlib.metadata
import json
import logging
import os
import sys
from pathlib import Path

from jsonschema import ValidationError

from news_report import mcp_server
from news_report.adapters import build_adapter_registry
from news_report.briefing import generate_briefing, validate_request
from news_report.catalog import SCHEMAS_DIR, load_json, load_sources, validate_sources
from news_report.formatter import format_briefing_markdown
from scripts.build_catalog import render_catalog

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "docs" / "catalog.md"

SCHEMA_ALIASES = {
    "briefing-request": "briefing-request.schema.json",
    "briefing-response": "briefing-response.schema.json",
    "source": "source.schema.json",
}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _write_json(data: object) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _read_request_json(path_arg: str | None, parser: argparse.ArgumentParser) -> object:
    """Read a briefing request from a file, stdin (`-`), or piped stdin."""
    if path_arg in (None, "-"):
        if path_arg is None and sys.stdin.isatty():
            parser.error("request_json is required unless JSON is piped on stdin")
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON from stdin: {exc.msg}") from exc

    return load_json(Path(path_arg).resolve())


def _render_source(source: dict) -> str:
    lines = [
        f"# {source['name']}",
        "",
        f"- id: `{source['id']}`",
        f"- url: {source['url']}",
        f"- category: `{source['category']}`",
        f"- interfaces: {', '.join(f'`{value}`' for value in source['interface_types'])}",
        f"- content types: {', '.join(f'`{value}`' for value in source['content_types'])}",
        f"- open source: `{'yes' if source['open_source'] else 'no'}`",
        f"- agent friendly: `{source['agent_friendly']}`",
        f"- pricing: `{source['pricing']}`",
        f"- stage: `{source['stage']}`",
        f"- last verified: `{source['last_verified']}`",
        "",
        source["summary"],
    ]
    notes = source.get("notes", [])
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines).rstrip() + "\n"


def _load_valid_sources() -> list[dict]:
    return validate_sources(load_sources())


def _select_sources(source_ids: list[str] | None = None) -> tuple[list[dict], list[str]]:
    sources = _load_valid_sources()
    if not source_ids:
        return sources, []

    by_id = {source["id"]: source for source in sources}
    selected = [by_id[source_id] for source_id in source_ids if source_id in by_id]
    missing = [source_id for source_id in source_ids if source_id not in by_id]
    return selected, missing


def _schema_paths() -> list[Path]:
    return sorted(SCHEMAS_DIR.glob("*.schema.json"))


def _schema_alias(path: Path) -> str:
    suffix = ".schema.json"
    return path.name[: -len(suffix)] if path.name.endswith(suffix) else path.stem


def _resolve_schema_path(name: str) -> Path:
    candidate_name = SCHEMA_ALIASES.get(name, name)
    candidates = [candidate_name]
    if not candidate_name.endswith(".json"):
        candidates.append(f"{candidate_name}.schema.json")
        candidates.append(f"{candidate_name}.json")

    for candidate in candidates:
        path = SCHEMAS_DIR / candidate
        if path.exists() and path.is_file():
            return path

    known = ", ".join(_schema_alias(path) for path in _schema_paths())
    raise ValueError(f"Unknown schema {name!r}. Known schemas: {known}")


# ---------------------------------------------------------------------------
# Existing console scripts
# ---------------------------------------------------------------------------


def build_catalog_cli() -> int:
    sources = _load_valid_sources()
    rendered = render_catalog(sources)
    CATALOG_PATH.write_text(rendered, encoding="utf-8")
    print(f"validated {len(sources)} sources")
    print(f"wrote {CATALOG_PATH.relative_to(ROOT)}")
    return 0


def _check_sources_cli(source_ids: list[str] | None = None, *, json_output: bool = False) -> int:
    """Ping source adapters and report health."""
    selected, missing = _select_sources(source_ids)
    registry = build_adapter_registry(selected)
    results: list[dict[str, str]] = []

    for missing_id in missing:
        results.append(
            {
                "source_id": missing_id,
                "name": missing_id,
                "adapter": "none",
                "status": "unknown_source",
            }
        )

    for source in selected:
        source_id = source["id"]
        adapter = registry[source_id]
        ok = adapter.ping()
        results.append(
            {
                "source_id": source_id,
                "name": source["name"],
                "adapter": type(adapter).__name__,
                "status": "ok" if ok else "unreachable",
            }
        )

    if json_output:
        _write_json(results)
    else:
        for result in results:
            status = "OK" if result["status"] == "ok" else "FAIL"
            print(f"  {status}  {result['source_id']} ({result['adapter']})")

    return 0 if all(result["status"] == "ok" for result in results) else 1


def generate_briefing_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="generate-briefing", description="Generate a news briefing.")
    parser.add_argument("request_json", nargs="?", help="Path to request JSON, or '-' / omitted for stdin")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", dest="output_format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    parser.add_argument("--check-sources", action="store_true", help="Ping sources and exit")
    parser.add_argument("--json", action="store_true", help="Use JSON output with --check-sources")

    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    if args.check_sources:
        return _check_sources_cli(json_output=args.json)

    try:
        request = validate_request(_read_request_json(args.request_json, parser))
        sources = _load_valid_sources()
        briefing = generate_briefing(request, sources)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output_format == "markdown":
        sys.stdout.write(format_briefing_markdown(briefing))
    else:
        _write_json(briefing)
    return 0


# ---------------------------------------------------------------------------
# Unified `news-report` CLI
# ---------------------------------------------------------------------------


def _briefing_generate(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    try:
        request = validate_request(_read_request_json(args.request_json, parser))
        briefing = generate_briefing(request, _load_valid_sources())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output_format == "markdown":
        sys.stdout.write(format_briefing_markdown(briefing))
    else:
        _write_json(briefing)
    return 0


def _sources_list(args: argparse.Namespace) -> int:
    try:
        sources = _load_valid_sources()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _write_json(sources)
        return 0

    for source in sources:
        interfaces = ",".join(source["interface_types"])
        print(f"{source['id']:<34} {source['category']:<22} {interfaces:<16} {source['summary']}")
    return 0


def _sources_get(args: argparse.Namespace) -> int:
    try:
        sources = _load_valid_sources()
        by_id = {source["id"]: source for source in sources}
        source = by_id[args.source_id]
    except KeyError:
        print(f"error: unknown source id: {args.source_id}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _write_json(source)
    else:
        sys.stdout.write(_render_source(source))
    return 0


def _sources_check(args: argparse.Namespace) -> int:
    try:
        return _check_sources_cli(args.source_ids, json_output=args.json)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _schemas_list(args: argparse.Namespace) -> int:
    schemas = [{"name": _schema_alias(path), "file": path.name} for path in _schema_paths()]
    if args.json:
        _write_json(schemas)
    else:
        for schema in schemas:
            print(f"{schema['name']:<20} {schema['file']}")
    return 0


def _schemas_get(args: argparse.Namespace) -> int:
    try:
        schema = load_json(_resolve_schema_path(args.schema_name))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    _write_json(schema)
    return 0


def _mcp_serve(_args: argparse.Namespace) -> int:
    mcp_server.main()
    return 0


def _doctor_check(name: str, status: str, message: str, *, hint: str | None = None) -> dict[str, str]:
    check = {"name": name, "status": status, "message": message}
    if hint:
        check["hint"] = hint
    return check


def _version_string() -> str:
    try:
        return importlib.metadata.version("news-report")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _doctor(args: argparse.Namespace) -> int:
    checks: list[dict[str, str]] = []
    sources: list[dict] = []

    checks.append(_doctor_check("package", "pass", f"news-report {_version_string()}"))

    try:
        sources = _load_valid_sources()
        checks.append(_doctor_check("sources", "pass", f"validated {len(sources)} sources"))
    except Exception as exc:
        checks.append(
            _doctor_check("sources", "fail", str(exc), hint="Fix data/sources.json or schemas/source.schema.json")
        )

    try:
        schema_files = _schema_paths()
        for path in schema_files:
            load_json(path)
        checks.append(_doctor_check("schemas", "pass", f"loaded {len(schema_files)} schema files"))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        checks.append(_doctor_check("schemas", "fail", str(exc), hint="Check schemas/*.schema.json"))

    try:
        _ = mcp_server.main
        checks.append(_doctor_check("mcp", "pass", "MCP server imports successfully"))
    except Exception as exc:
        checks.append(_doctor_check("mcp", "fail", str(exc), hint="Run `uv run news-report-mcp` for details"))

    rsshub_base = os.environ.get("RSSHUB_BASE_URL", "https://rsshub.app")
    if args.skip_network:
        checks.append(_doctor_check("rsshub", "warn", f"network check skipped; base URL would be {rsshub_base}"))
    elif sources:
        rsshub_sources = [source for source in sources if source["id"] == "rsshub"]
        if rsshub_sources:
            try:
                adapter = build_adapter_registry(rsshub_sources)["rsshub"]
                ok = adapter.ping()
                checks.append(
                    _doctor_check(
                        "rsshub",
                        "pass" if ok else "warn",
                        f"{rsshub_base} is reachable" if ok else f"{rsshub_base} is not reachable",
                        hint=None if ok else "Set RSSHUB_BASE_URL to a reachable instance or retry later",
                    )
                )
            except Exception as exc:
                checks.append(
                    _doctor_check(
                        "rsshub",
                        "warn",
                        f"RSSHub check failed: {exc}",
                        hint="Set RSSHUB_BASE_URL to a reachable instance or retry later",
                    )
                )

    failed = [check for check in checks if check["status"] == "fail"]
    warned = [check for check in checks if check["status"] == "warn"]
    summary = {"passed": len(checks) - len(failed) - len(warned), "warnings": len(warned), "failed": len(failed)}

    if args.json:
        _write_json({"checks": checks, "summary": summary})
    else:
        for check in checks:
            symbol = {"pass": "✔", "warn": "!", "fail": "✘"}.get(check["status"], "?")
            print(f"{symbol} {check['name']:<12} {check['message']}")
            if "hint" in check:
                print(f"  hint: {check['hint']}")
        print(f"\n{summary['passed']} passed, {summary['warnings']} warnings, {summary['failed']} failed")

    return 1 if failed else 0


def _catalog_build(_args: argparse.Namespace) -> int:
    try:
        return build_catalog_cli()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _add_briefing_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    briefing = subparsers.add_parser("briefing", help="Generate and inspect briefings")
    briefing_sub = briefing.add_subparsers(dest="briefing_command", required=True)

    generate_parser = briefing_sub.add_parser("generate", help="Generate a briefing from request JSON")
    generate_parser.add_argument("request_json", nargs="?", help="Path to request JSON, or '-' / omitted for stdin")
    generate_parser.add_argument("--format", choices=["json", "markdown"], default="json", dest="output_format")
    generate_parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    generate_parser.set_defaults(func=lambda args: _briefing_generate(args, generate_parser))


def _add_sources_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    sources = subparsers.add_parser("sources", help="List, inspect, and check source adapters")
    sources_sub = sources.add_subparsers(dest="sources_command", required=True)

    list_parser = sources_sub.add_parser("list", help="List available sources")
    list_parser.add_argument("--json", action="store_true", help="Output full source records as JSON")
    list_parser.set_defaults(func=_sources_list)

    get_parser = sources_sub.add_parser("get", help="Show one source")
    get_parser.add_argument("source_id")
    get_parser.add_argument("--json", action="store_true", help="Output the full source record as JSON")
    get_parser.set_defaults(func=_sources_get)

    check_parser = sources_sub.add_parser("check", help="Ping source adapters")
    check_parser.add_argument("source_ids", nargs="*", help="Optional source IDs. Checks all sources when omitted")
    check_parser.add_argument("--json", action="store_true", help="Output health checks as JSON")
    check_parser.set_defaults(func=_sources_check)


def _add_schemas_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    schemas = subparsers.add_parser("schemas", help="List and print JSON Schemas")
    schemas_sub = schemas.add_subparsers(dest="schemas_command", required=True)

    list_parser = schemas_sub.add_parser("list", help="List schemas")
    list_parser.add_argument("--json", action="store_true", help="Output schema list as JSON")
    list_parser.set_defaults(func=_schemas_list)

    get_parser = schemas_sub.add_parser("get", help="Print a schema")
    get_parser.add_argument("schema_name", help="Schema alias, e.g. briefing-request, briefing-response, source")
    get_parser.add_argument("--json", action="store_true", help="Kept for command consistency; output is always JSON")
    get_parser.set_defaults(func=_schemas_get)


def _add_mcp_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    mcp = subparsers.add_parser("mcp", help="Run MCP server commands")
    mcp_sub = mcp.add_subparsers(dest="mcp_command", required=True)

    serve_parser = mcp_sub.add_parser("serve", help="Run the News Report MCP server over stdio")
    serve_parser.set_defaults(func=_mcp_serve)


def _add_catalog_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    catalog = subparsers.add_parser("catalog", help="Build the generated resource catalog")
    catalog_sub = catalog.add_subparsers(dest="catalog_command", required=True)

    build_parser = catalog_sub.add_parser("build", help="Regenerate docs/catalog.md")
    build_parser.set_defaults(func=_catalog_build)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="news-report",
        description="Agent-native briefing compiler CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    _add_briefing_parser(subparsers)
    _add_sources_parser(subparsers)
    _add_schemas_parser(subparsers)
    _add_mcp_parser(subparsers)
    _add_catalog_parser(subparsers)

    doctor_parser = subparsers.add_parser("doctor", help="Check the local News Report setup")
    doctor_parser.add_argument("--json", action="store_true", help="Output checks as JSON")
    doctor_parser.add_argument("--skip-network", action="store_true", help="Skip RSSHub reachability checks")
    doctor_parser.set_defaults(func=_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
