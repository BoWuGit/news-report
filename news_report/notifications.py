from __future__ import annotations

import platform
import shlex
import subprocess


def _applescript_string_literal(value: str) -> str:
    """AppleScript string literals use double quotes; escape \\ and \"."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_notification_command(title: str, body: str, subtitle: str = "", sound: str = "") -> list[str]:
    system = platform.system()

    if system == "Darwin":
        parts = [
            f"display notification {_applescript_string_literal(body)}",
            f"with title {_applescript_string_literal(title)}",
        ]
        if subtitle:
            parts.append(f"subtitle {_applescript_string_literal(subtitle)}")
        if sound:
            parts.append(f"sound name {_applescript_string_literal(sound)}")
        return ["osascript", "-e", " ".join(parts)]

    if system == "Linux":
        summary = title if not subtitle else f"{title} - {subtitle}"
        return ["notify-send", summary, body]

    if system == "Windows":
        escaped_title = title.replace("'", "''")
        escaped_body = body.replace("'", "''")
        escaped_subtitle = subtitle.replace("'", "''")
        tip_text = f"{escaped_subtitle}: {escaped_body}" if escaped_subtitle else escaped_body
        lines = [
            "Add-Type -AssemblyName System.Windows.Forms",
            "$notify = New-Object System.Windows.Forms.NotifyIcon",
            "$notify.Icon = [System.Drawing.SystemIcons]::Information",
            f"$notify.BalloonTipTitle = '{escaped_title}'",
            f"$notify.BalloonTipText = '{tip_text}'",
            "$notify.Visible = $true",
            "$notify.ShowBalloonTip(5000)",
        ]
        return ["powershell", "-NoProfile", "-Command", "; ".join(lines)]

    raise RuntimeError(f"Unsupported platform: {system}")


def send_notification(title: str, body: str, subtitle: str = "", sound: str = "") -> None:
    cmd = build_notification_command(title=title, body=body, subtitle=subtitle, sound=sound)
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def shell_preview(title: str, body: str, subtitle: str = "", sound: str = "") -> str:
    return shlex.join(build_notification_command(title=title, body=body, subtitle=subtitle, sound=sound))
