#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_SRC = ROOT / "packages" / "social_timeline_runtime" / "src"
if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from social_timeline_runtime.notifications import send_notification, shell_preview


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a best-effort desktop notification.")
    parser.add_argument("--title", required=True, help="Notification title.")
    parser.add_argument("--body", required=True, help="Notification body.")
    parser.add_argument("--subtitle", default="", help="Optional subtitle.")
    parser.add_argument("--sound", default="", help="Optional sound hint for platforms that support it.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the underlying platform command instead of executing it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dry_run:
        print(shell_preview(title=args.title, body=args.body, subtitle=args.subtitle, sound=args.sound))
        return 0

    try:
        send_notification(title=args.title, body=args.body, subtitle=args.subtitle, sound=args.sound)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
