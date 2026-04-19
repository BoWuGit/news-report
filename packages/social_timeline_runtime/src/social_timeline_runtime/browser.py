"""Minimal Chrome DevTools Protocol client for the social timeline runtime.

The published skill should not depend on IDE-specific MCP wiring. This client
talks directly to Chrome's remote-debugging HTTP and WebSocket endpoints so the
runtime can own browser automation behavior.

Chrome 147+ requires ``--user-data-dir`` for remote debugging. This module
manages a dedicated profile directory so that login sessions persist across
runs without touching the user's default Chrome profile.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Dedicated profile directory — keeps login sessions across runs.
_DEFAULT_PROFILE_DIR = Path.home() / ".news-report" / "chrome-profile"
_DEFAULT_PORT = 9222
_LAUNCH_WAIT_SECONDS = 6
_LAUNCH_POLL_INTERVAL = 0.5


@dataclass(frozen=True)
class PageTarget:
    id: str
    title: str
    url: str
    web_socket_debugger_url: str


class ChromeDebugError(RuntimeError):
    """Raised when the runtime cannot talk to Chrome's remote debug endpoint."""


class ChromeRemote:
    """Tiny synchronous CDP wrapper for one-off automation tasks."""

    def __init__(self, base_url: str = "http://127.0.0.1:9222"):
        self.base_url = base_url.rstrip("/")

    def _get_json(self, path: str) -> object:
        url = f"{self.base_url}{path}"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ChromeDebugError(f"Could not reach Chrome debug endpoint at {self.base_url}") from exc

    def list_pages(self) -> list[PageTarget]:
        payload = self._get_json("/json")
        if not isinstance(payload, list):
            raise ChromeDebugError("Unexpected response from /json")

        pages = []
        for item in payload:
            if not isinstance(item, dict) or item.get("type") != "page":
                continue
            ws_url = item.get("webSocketDebuggerUrl")
            if not isinstance(ws_url, str) or not ws_url:
                continue
            pages.append(
                PageTarget(
                    id=str(item.get("id", "")),
                    title=str(item.get("title", "")),
                    url=str(item.get("url", "")),
                    web_socket_debugger_url=ws_url,
                )
            )
        return pages

    def get_or_create_page(self, target_url: str) -> PageTarget:
        for page in self.list_pages():
            if page.url.startswith(target_url):
                return page
        page = self.open_page(target_url)
        if not page.url.startswith(target_url):
            self.navigate(page, target_url)
            return PageTarget(
                id=page.id,
                title=page.title,
                url=target_url,
                web_socket_debugger_url=page.web_socket_debugger_url,
            )
        return page

    def open_page(self, target_url: str) -> PageTarget:
        encoded = urllib.parse.quote(target_url, safe=":/?&=%")
        request = urllib.request.Request(f"{self.base_url}/json/new?{encoded}", method="PUT")
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ChromeDebugError(f"Could not open a new Chrome page via {self.base_url}") from exc
        if not isinstance(payload, dict):
            raise ChromeDebugError("Unexpected response from /json/new")
        ws_url = payload.get("webSocketDebuggerUrl")
        if not isinstance(ws_url, str) or not ws_url:
            raise ChromeDebugError("New page response did not include webSocketDebuggerUrl")
        return PageTarget(
            id=str(payload.get("id", "")),
            title=str(payload.get("title", "")),
            url=str(payload.get("url", "")),
            web_socket_debugger_url=ws_url,
        )

    def navigate(self, page: PageTarget, target_url: str) -> None:
        session = CDPSession(page.web_socket_debugger_url)
        try:
            session.send("Page.enable")
            session.send("Runtime.enable")
            session.send("Page.navigate", {"url": target_url})
            session.wait_for_load()
        finally:
            session.close()


class CDPSession:
    """Synchronous helper around a single page WebSocket."""

    def __init__(self, ws_url: str):
        try:
            from websocket import create_connection  # noqa: PLC0415  # lazy: optional dep

            # Chrome 147 rejects the default Origin header from websocket-client
            # unless remote-allow-origins is explicitly widened. Suppressing the
            # header keeps the runtime self-contained and avoids requiring extra
            # browser flags for local CLI usage.
            self._ws = create_connection(ws_url, timeout=10, suppress_origin=True)
        except Exception as exc:  # pragma: no cover - network exception types vary
            raise ChromeDebugError("Could not connect to Chrome page websocket") from exc
        self._next_id = 0

    def close(self) -> None:
        self._ws.close()

    def send(self, method: str, params: dict | None = None) -> object:
        self._next_id += 1
        message_id = self._next_id
        self._ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            raw = self._ws.recv()
            payload = json.loads(raw)
            if payload.get("id") != message_id:
                continue
            if "error" in payload:
                message = payload["error"].get("message", "CDP command failed")
                raise ChromeDebugError(message)
            return payload.get("result")

    def wait_for_load(self, timeout_ms: int = 10000) -> None:
        self.send("Runtime.evaluate", {"expression": "document.readyState"})
        self.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    new Promise((resolve) => {{
                      if (document.readyState === 'complete') {{ resolve(true); return; }}
                      const done = () => resolve(true);
                      window.addEventListener('load', done, {{ once: true }});
                      setTimeout(() => resolve(false), {timeout_ms});
                    }})
                """,
                "awaitPromise": True,
                "returnByValue": True,
            },
        )

    def evaluate(self, expression: str) -> object:
        result = self.send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": True,
                "returnByValue": True,
            },
        )
        if not isinstance(result, dict):
            return result
        output = result.get("result", {})
        if isinstance(output, dict) and "value" in output:
            return output["value"]
        return output


# ---------------------------------------------------------------------------
# Chrome auto-launch
# ---------------------------------------------------------------------------


def _find_chrome_binary() -> str | None:
    """Return the path to a Chrome binary, or None if not found."""
    system = platform.system()
    if system == "Darwin":
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.isfile(path):
            return path
    elif system == "Linux":
        for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
            found = shutil.which(name)
            if found:
                return found
    elif system == "Windows":
        for base in (os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", "")):
            if not base:
                continue
            path = os.path.join(base, "Google", "Chrome", "Application", "chrome.exe")
            if os.path.isfile(path):
                return path
    return shutil.which("google-chrome") or shutil.which("chrome")


def _is_debug_port_alive(port: int) -> bool:
    """Return True if Chrome's debug HTTP endpoint is responding."""
    try:
        url = f"http://127.0.0.1:{port}/json/version"
        with urllib.request.urlopen(url, timeout=2):
            return True
    except Exception:
        return False


def ensure_chrome(
    port: int = _DEFAULT_PORT,
    profile_dir: Path | None = None,
) -> ChromeRemote:
    """Return a ChromeRemote connected to a debug-enabled Chrome instance.

    If no Chrome is listening on *port*, one is launched automatically using a
    dedicated ``--user-data-dir`` so that remote debugging works on Chrome 147+
    and login sessions persist across runs.
    """
    base_url = f"http://127.0.0.1:{port}"

    if _is_debug_port_alive(port):
        return ChromeRemote(base_url)

    chrome_bin = _find_chrome_binary()
    if chrome_bin is None:
        raise ChromeDebugError("Could not find a Chrome binary. Install Google Chrome or set PATH.")

    profile = profile_dir or _DEFAULT_PROFILE_DIR
    profile.mkdir(parents=True, exist_ok=True)

    cmd = [
        chrome_bin,
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={profile}",
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    deadline = time.monotonic() + _LAUNCH_WAIT_SECONDS
    while time.monotonic() < deadline:
        if _is_debug_port_alive(port):
            return ChromeRemote(base_url)
        time.sleep(_LAUNCH_POLL_INTERVAL)

    raise ChromeDebugError(f"Launched Chrome but debug port {port} did not respond within {_LAUNCH_WAIT_SECONDS}s")
