"""Notification bridge for the social timeline runtime.

The runtime owns the CLI contract. Platform-specific notification behavior is
temporarily delegated to the existing implementation until migration finishes.
"""

from __future__ import annotations

from news_report.notifications import build_notification_command, send_notification, shell_preview

__all__ = ["build_notification_command", "send_notification", "shell_preview"]
