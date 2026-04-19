"""Site-specific login detection and extraction routines."""

from __future__ import annotations

from dataclasses import dataclass

from social_timeline_runtime.browser import CDPSession, ChromeRemote, PageTarget
from social_timeline_runtime.normalize import JIKE_EXTRACTION_SCRIPT, X_EXTRACTION_SCRIPT

X_HOME_URL = "https://x.com/home"
JIKE_FOLLOWING_URL = "https://web.okjike.com/following"
X_SCROLL_WAIT_MS = 2000
JIKE_SCROLL_WAIT_MS = 1200


@dataclass(frozen=True)
class LoginStatus:
    site: str
    logged_in: bool
    page_url: str
    title: str
    reason: str


def target_url_for(site: str) -> str:
    if site == "x":
        return X_HOME_URL
    if site == "jike":
        return JIKE_FOLLOWING_URL
    raise ValueError(f"Unsupported site: {site}")


def ensure_site_page(chrome: ChromeRemote, site: str) -> PageTarget:
    target_url = target_url_for(site)
    return chrome.get_or_create_page(target_url)


def inspect_login(chrome: ChromeRemote, site: str) -> LoginStatus:
    page = ensure_site_page(chrome, site)
    snapshot = _run_on_page(page, _capture_login_snapshot)

    if not isinstance(snapshot, dict):
        raise RuntimeError("Unexpected login inspection payload")

    if site == "x":
        return _detect_x_login(snapshot)
    return _detect_jike_login(snapshot)


def _detect_x_login(snapshot: dict) -> LoginStatus:
    url = str(snapshot.get("url", ""))
    title = str(snapshot.get("title", ""))
    body = str(snapshot.get("body", ""))
    article_count = int(snapshot.get("articleCount", 0) or 0)
    lower = f"{url}\n{title}\n{body}".lower()

    if any(token in lower for token in ["/login", "/i/flow/login", "create account", "sign in", "log in"]):
        return LoginStatus(site="x", logged_in=False, page_url=url, title=title, reason="login_prompt")
    if "refuse all" in lower or "accept all" in lower:
        return LoginStatus(site="x", logged_in=False, page_url=url, title=title, reason="cookie_banner_or_blocked")
    if article_count > 0:
        return LoginStatus(site="x", logged_in=True, page_url=url, title=title, reason="timeline_visible")
    return LoginStatus(site="x", logged_in=False, page_url=url, title=title, reason="timeline_not_visible")


def _detect_jike_login(snapshot: dict) -> LoginStatus:
    url = str(snapshot.get("url", ""))
    title = str(snapshot.get("title", ""))
    body = str(snapshot.get("body", ""))
    viewport_text = str(snapshot.get("viewportText", ""))
    lower = f"{url}\n{title}\n{body}\n{viewport_text}".lower()

    if any(token in lower for token in ["/login", "扫码登录", "手机号登录", "登录即刻"]):
        return LoginStatus(site="jike", logged_in=False, page_url=url, title=title, reason="login_prompt")
    if viewport_text.strip():
        return LoginStatus(site="jike", logged_in=True, page_url=url, title=title, reason="timeline_visible")
    return LoginStatus(site="jike", logged_in=False, page_url=url, title=title, reason="timeline_not_visible")


def scrape_site(chrome: ChromeRemote, site: str) -> dict:
    page = ensure_site_page(chrome, site)
    items = _run_on_page(page, _scrape_x if site == "x" else _scrape_jike)
    return {"site": site, "page_url": page.url, "items": items}


def _scrape_x(session: CDPSession) -> list[dict]:
    _ensure_x_following_latest(session)
    items: dict[str, dict] = {}
    for _ in range(3):
        round_items = _evaluate_item_list(session, X_EXTRACTION_SCRIPT, "X")
        added = _merge_unique_items(items, round_items)
        if added == 0:
            break
        session.evaluate("window.scrollBy(0, 3000)")
        _sleep(session, X_SCROLL_WAIT_MS)
    return list(items.values())


def _ensure_x_following_latest(session: CDPSession) -> None:
    """Switch X timeline to the Following tab sorted by Latest.

    Idempotent — no-ops when the tab and sort order are already correct.
    """
    # Activate the "Following" / "正在关注" tab if not already selected.
    # X renders tabs as <div role="tab"> inside [role="tablist"].
    session.evaluate(
        """
        (() => {
          const tab = Array.from(document.querySelectorAll('[role="tablist"] [role="tab"]'))
            .find(t => /正在关注|^Following$/.test(t.innerText.trim()));
          if (tab && tab.getAttribute('aria-selected') !== 'true') tab.click();
        })()
        """
    )
    _sleep(session, 1500)

    # Click the selected tab again to open its sort dropdown
    # (the tab carries aria-haspopup="menu").
    session.evaluate(
        """
        (() => {
          const tab = Array.from(document.querySelectorAll('[role="tablist"] [role="tab"]'))
            .find(t => /正在关注|^Following$/.test(t.innerText.trim()));
          if (tab && tab.getAttribute('aria-selected') === 'true') tab.click();
        })()
        """
    )
    _sleep(session, 800)

    # Pick "Latest" / "最近" from the sort menu.
    session.evaluate(
        """
        (() => {
          const item = Array.from(document.querySelectorAll('[role="menuitem"]'))
            .find(el => /^(最近|Latest)$/.test(el.innerText.trim()));
          if (item) item.click();
        })()
        """
    )
    _sleep(session, 1500)


def _scrape_jike(session: CDPSession) -> list[dict]:
    chunks: dict[str, dict] = {}
    for _ in range(15):
        round_items = _evaluate_item_list(session, JIKE_EXTRACTION_SCRIPT, "Jike")
        _merge_unique_items(chunks, round_items, key_field="text")

        scroll = session.evaluate(
            """
            (() => {
              const viewport = document.querySelector('.mantine-ScrollArea-viewport');
              if (!viewport) return { moved: false, reason: 'viewport_missing' };
              const before = viewport.scrollTop;
              viewport.scrollTop += viewport.clientHeight * 0.8;
              return { moved: viewport.scrollTop !== before, top: viewport.scrollTop };
            })()
            """
        )
        moved = isinstance(scroll, dict) and bool(scroll.get("moved"))
        if not moved:
            break
        _sleep(session, JIKE_SCROLL_WAIT_MS)
    return list(chunks.values())


def _run_on_page(page: PageTarget, action) -> object:
    session = CDPSession(page.web_socket_debugger_url)
    try:
        session.send("Runtime.enable")
        session.send("Page.enable")
        session.wait_for_load()
        return action(session)
    finally:
        session.close()


def _capture_login_snapshot(session: CDPSession) -> object:
    return session.evaluate(
        """
        (() => ({
          url: location.href,
          title: document.title || '',
          body: (document.body?.innerText || '').slice(0, 4000),
          articleCount: document.querySelectorAll('article').length,
          viewportText: document.querySelector('.mantine-ScrollArea-viewport')?.innerText?.slice(0, 4000) || ''
        }))()
        """
    )


def _evaluate_item_list(session: CDPSession, script: str, site_name: str) -> list[dict]:
    # Extraction scripts are arrow-function expressions; wrap as IIFE so
    # Runtime.evaluate returns the function's *return value*, not the
    # function object itself (which serialises to {}).
    expression = f"({script.strip()})()"
    round_items = session.evaluate(expression)
    if isinstance(round_items, str):
        raise RuntimeError(f"{site_name} extraction script returned a JSON string; expected an array")
    if not isinstance(round_items, list):
        raise RuntimeError(f"{site_name} extraction script returned an unexpected payload")
    return [item for item in round_items if isinstance(item, dict)]


def _merge_unique_items(existing: dict[str, dict], incoming: list[dict], key_field: str = "url") -> int:
    added = 0
    for item in incoming:
        key = str(item.get(key_field) or item.get("text") or "").strip()
        if not key or key in existing:
            continue
        existing[key] = item
        added += 1
    return added


def _sleep(session: CDPSession, duration_ms: int) -> None:
    session.evaluate(f"new Promise((resolve) => setTimeout(resolve, {duration_ms}))")
