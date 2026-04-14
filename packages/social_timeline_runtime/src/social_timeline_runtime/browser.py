"""Minimal Chrome DevTools Protocol client for the social timeline runtime.

The published skill should not depend on IDE-specific MCP wiring. This client
talks directly to Chrome's remote-debugging HTTP and WebSocket endpoints so the
runtime can own browser automation behavior.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


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
