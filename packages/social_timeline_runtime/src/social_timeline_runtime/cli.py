"""CLI contract for the future standalone social timeline runtime.

The command surface is intentionally small and stable. Some subcommands are
scaffolds today: they define the expected interface even before browser
automation has fully moved out of `news_report`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from social_timeline_runtime.agent_backend import run_agent_task
from social_timeline_runtime.browser import ChromeDebugError, ChromeRemote
from social_timeline_runtime.normalize import normalize_jike_posts, normalize_x_posts
from social_timeline_runtime.notifications import send_notification
from social_timeline_runtime.sites import inspect_login, scrape_site

JsonCommand = Callable[[argparse.Namespace], int]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="social-timeline", description="Runtime for social timeline scraping skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_login = subparsers.add_parser("check-login", help="Validate that a site session is present.")
    check_login.add_argument("--site", choices=["x", "jike"], required=True)
    check_login.add_argument("--chrome-url", default="http://127.0.0.1:9222")

    scrape = subparsers.add_parser("scrape", help="Capture raw timeline data from a site.")
    scrape.add_argument("--site", choices=["x", "jike"], required=True)
    scrape.add_argument("--output", required=True)
    scrape.add_argument("--chrome-url", default="http://127.0.0.1:9222")
    scrape.add_argument(
        "--max-items", type=int, default=0, help="Limit the raw items written to disk. 0 means no limit."
    )

    normalize = subparsers.add_parser("normalize", help="Convert raw timeline data into candidate items.")
    normalize.add_argument("--site", choices=["x", "jike"], required=True)
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--output", required=True)
    normalize.add_argument("--source-id", required=True)
    normalize.add_argument("--source-name", required=True)

    notify = subparsers.add_parser("notify", help="Send a local system notification.")
    notify.add_argument("--title", required=True)
    notify.add_argument("--body", required=True)
    notify.add_argument("--subtitle", default="")
    notify.add_argument("--sound", default="")

    run_agent = subparsers.add_parser("run-agent", help="Run a prompt through a configured agent backend.")
    run_agent.add_argument("--backend", choices=["auto", "codex", "claude", "fallback"], default="auto")
    run_agent.add_argument("--input", required=True)
    run_agent.add_argument("--output", required=True)
    run_agent.add_argument("--fallback-text", default="Manual attention required.")
    run_agent.add_argument("--strict", action="store_true")

    return parser


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")


def _json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _cmd_check_login(args: argparse.Namespace) -> int:
    try:
        status = inspect_login(ChromeRemote(args.chrome_url), args.site)
    except ChromeDebugError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(_json_text(status.__dict__))
    return 0 if status.logged_in else 2


def _cmd_scrape(args: argparse.Namespace) -> int:
    try:
        payload = scrape_site(ChromeRemote(args.chrome_url), args.site)
    except ChromeDebugError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.max_items and isinstance(payload.get("items"), list):
        payload["items"] = payload["items"][: args.max_items]
    payload["captured_at"] = datetime.now(UTC).isoformat()
    _write_json(Path(args.output), payload)
    return 0


def _cmd_normalize(args: argparse.Namespace) -> int:
    payload = _read_json(Path(args.input))
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        print("error: normalize input must be an object with an 'items' list", file=sys.stderr)
        return 1

    source_meta = {"id": args.source_id, "name": args.source_name}
    now = datetime.now(UTC)
    items = payload["items"]
    if args.site == "x":
        candidates = normalize_x_posts(items, source_meta=source_meta, now=now)
    else:
        candidates = normalize_jike_posts(items, source_meta=source_meta, now=now)

    _write_json(Path(args.output), candidates)
    return 0


def _cmd_notify(args: argparse.Namespace) -> int:
    send_notification(args.title, args.body, subtitle=args.subtitle, sound=args.sound)
    return 0


def _cmd_run_agent(args: argparse.Namespace) -> int:
    code, message = run_agent_task(
        backend=args.backend,
        input_path=Path(args.input),
        output_path=Path(args.output),
        fallback_text=args.fallback_text,
        strict=args.strict,
    )
    stream = sys.stderr if message.startswith("error:") else sys.stdout
    print(message, file=stream)
    return code


def _json_text(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, default=_json_default)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    commands: dict[str, JsonCommand] = {
        "check-login": _cmd_check_login,
        "scrape": _cmd_scrape,
        "normalize": _cmd_normalize,
        "notify": _cmd_notify,
        "run-agent": _cmd_run_agent,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
