from __future__ import annotations

import unittest
from unittest.mock import patch

from news_report.notifications import build_notification_command, send_notification


class NotificationCommandTests(unittest.TestCase):
    @patch("platform.system", return_value="Darwin")
    def test_build_macos_notification_command(self, _mock_system: object) -> None:
        cmd = build_notification_command(
            title="News Report",
            body="Please log in.",
            subtitle="Need Login",
            sound="Ping",
        )
        self.assertEqual(cmd[:2], ["osascript", "-e"])
        self.assertIn("display notification", cmd[2])
        self.assertIn("Need Login", cmd[2])
        self.assertIn("Ping", cmd[2])

    @patch("platform.system", return_value="Darwin")
    def test_build_macos_escapes_quotes_for_applescript(self, _mock_system: object) -> None:
        cmd = build_notification_command(title="T", body='He said "go"', subtitle="", sound="")
        self.assertEqual(cmd[:2], ["osascript", "-e"])
        self.assertIn('display notification "He said \\"go\\""', cmd[2])

    @patch("platform.system", return_value="Linux")
    def test_build_linux_notification_command(self, _mock_system: object) -> None:
        cmd = build_notification_command(
            title="News Report",
            body="Please log in.",
            subtitle="Need Login",
        )
        self.assertEqual(cmd, ["notify-send", "News Report - Need Login", "Please log in."])

    @patch("platform.system", return_value="Windows")
    def test_build_windows_notification_command(self, _mock_system: object) -> None:
        cmd = build_notification_command(
            title="News Report",
            body="Please log in.",
            subtitle="Need Login",
        )
        self.assertEqual(cmd[:3], ["powershell", "-NoProfile", "-Command"])
        self.assertIn("BalloonTipTitle", cmd[3])
        self.assertIn("Need Login", cmd[3])

    @patch("platform.system", return_value="Plan9")
    def test_unknown_platform_raises(self, _mock_system: object) -> None:
        with self.assertRaisesRegex(RuntimeError, "Unsupported platform"):
            build_notification_command(title="News Report", body="Please log in.")

    @patch("news_report.notifications.subprocess.run")
    @patch("platform.system", return_value="Linux")
    def test_send_notification_executes_command(self, _mock_system: object, mock_run: object) -> None:
        send_notification(title="News Report", body="Please log in.", subtitle="Need Login")
        mock_run.assert_called_once_with(
            ["notify-send", "News Report - Need Login", "Please log in."],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
