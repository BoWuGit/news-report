---
name: scraping-social-timeline
description: "Scrapes authenticated social media timelines (X/Twitter, Jike) via Chrome DevTools Protocol and generates a structured briefing. Use when asked to summarize social feeds, generate timeline briefings, or extract content from logged-in social media pages."
---

# Scraping Social Media Timelines

Extracts and summarizes content from authenticated social media timelines using Chrome DevTools Protocol (CDP).

## Supported Sites

| Site | URL | Notes |
|------|-----|-------|
| X (Twitter) | `https://x.com/home` | "正在关注" tab recommended for personal timeline |
| 即刻 (Jike) | `https://web.okjike.com/following` | Web version has limited lazy loading |

## Prerequisites

- User must be logged into the target sites in the connected Chrome browser
- Chrome DevTools MCP must be available (or equivalent CDP tool)
- CDP tool permissions should be pre-approved (see "Avoiding CDP Permission Prompts" below)

## Avoiding CDP Permission Prompts

每次调用 CDP 工具都需要人工确认会严重打断流程。下面只保留经过验证仍有参考价值的配置方式。

本 skill 只使用以下 CDP 工具（全部只读）：`list_pages`、`select_page`、`take_snapshot`、`evaluate_script`、`navigate_page`、`new_page`。

### Claude Code / Amp

在 `~/.claude/settings.json` 中添加：

```json
"permissions": [
  {"tool": "mcp__chrome_devtools__*", "action": "allow"}
]
```

⚠️ 注意：这是全局配置，会对所有项目生效。建议仅在受信任的个人环境使用，且不要在同一 Chrome profile 中同时打开银行、邮箱等敏感页面。

或在 `-x` 一次性任务中使用 `--dangerously-allow-all`：`amp --dangerously-allow-all -x "scrape my timeline"`

### Cursor

Cursor 的 MCP 工具审批通过 UI 设置控制：

1. 打开 **Cursor Settings → Features → Chat → Agent**
2. 在 **Auto-run** 部分启用 MCP 工具的自动执行
3. 或者在 Agent 模式中首次审批时选择 **"Always allow"** 对特定工具永久授权

### 方案：将 MCP 绑定到 skill 的 mcp.json（仅限 Claude Code）

在 skill 目录下创建 `mcp.json`，只暴露必要的工具（最小权限，无写入操作）：

```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": ["chrome-devtools-mcp@latest", "--autoConnect"],
    "includeTools": ["list_pages", "select_page", "take_snapshot", "evaluate_script", "navigate_page", "new_page"]
  }
}
```

## Workflow

### Step 0: Ensure Chrome is running with remote debugging

Before any CDP operations, verify Chrome is accessible.

#### Auto-suppress "Allow remote debugging?" dialog (Chrome 129+)

Chrome 129+ shows a security confirmation dialog every time an external app connects via CDP. To permanently suppress it, set the Chrome enterprise policy **before** launching Chrome:

```bash
# macOS — set once, persists across restarts
defaults write com.google.Chrome DevToolsRemoteDebuggingAllowed -bool true

# Linux — create policy file
sudo mkdir -p /etc/opt/chrome/policies/managed
echo '{"DevToolsRemoteDebuggingAllowed": true}' | sudo tee /etc/opt/chrome/policies/managed/devtools.json
```

Check if already set: `defaults read com.google.Chrome DevToolsRemoteDebuggingAllowed`
If not set or `0`, set it and restart Chrome. **Requires Chrome restart to take effect.**

#### Chrome connection check:

1. Call `list_pages` to test CDP connection
2. **If connection fails** (e.g., "Could not connect to Chrome" error):
   - Detect OS using `uname`:
     - **macOS**: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome`
     - **Linux**: `google-chrome` or `chromium-browser`
   - Check if Chrome is already running (non-debug mode):
     - macOS: `pgrep -x "Google Chrome"`
     - Linux: `pgrep -x chrome`
   - **If Chrome is running without debug port**:
     - Tell user: "⚠️ Chrome 正在运行但未开启调试端口。需要重启 Chrome 以启用远程调试。请先保存浏览器中未保存的工作，然后告诉我 'OK'，我将自动重启 Chrome。"
     - Wait for user confirmation, then:
       - macOS: `osascript -e 'quit app "Google Chrome"'` (graceful quit)
       - Wait 2 seconds, then launch with debug port
   - **If Chrome is not running at all**:
     - Auto-launch with debug port. **Must use direct binary path** (not `open -a`, which silently drops `--args` on macOS).
     - **Chrome 146+ requires `--user-data-dir`** — remote debugging is blocked on the default data directory.
     - **macOS Cookie encryption**: Chrome on macOS encrypts Cookies via Keychain (`Chrome Safe Storage`). Copying the default profile to a new `--user-data-dir` does NOT carry over login sessions — cookies become undecryptable. Symlinks also fail (Chrome resolves to real path). **The only viable approach is a persistent dedicated debug profile where the user logs in once.**
       ```bash
       # macOS
       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
         --remote-debugging-port=9222 \
         --remote-debugging-address=127.0.0.1 \
         --user-data-dir="$HOME/.chrome-debug-profile" \
         --no-first-run \
         --no-default-browser-check \
         &>/dev/null &
       # Linux (cookie encryption is different, profile copy MAY work)
       google-chrome \
         --remote-debugging-port=9222 \
         --remote-debugging-address=127.0.0.1 \
         --user-data-dir="$HOME/.chrome-debug-profile" \
         --no-first-run \
         --no-default-browser-check \
         &>/dev/null &
       ```
     - `--no-first-run` suppresses the "Welcome to Google Chrome" dialog on fresh profiles
     - `~/.chrome-debug-profile` is persistent — user only needs to log into sites **once**, cookies are retained across sessions
     - **First-time setup**: tell user "这是专用调试浏览器，首次使用需要登录一次目标网站（X、即刻等），之后登录态会自动保留。"

   - **Non-intrusive mode — minimize foreground disruption (macOS)**:
     - Use `--window-position=-32000,-32000` to place window off-screen at launch
     - Remember the current frontmost app and aggressively refocus it:
       ```bash
       # Save current app, launch Chrome off-screen, immediately hide + refocus
       CURRENT_APP=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true')
       
       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
         --remote-debugging-port=9222 \
         --remote-debugging-address=127.0.0.1 \
         --user-data-dir="$HOME/.chrome-debug-profile" \
         --no-first-run --no-default-browser-check \
         --window-position=-32000,-32000 \
         &>/dev/null &
       
       # Aggressively hide Chrome + refocus (loop catches delayed window creation)
       (for i in 1 2 3 4 5 6 7 8 9 10; do
         sleep 0.3
         osascript -e 'tell application "System Events" to set visible of process "Google Chrome" to false' 2>/dev/null
         osascript -e "tell application \"$CURRENT_APP\" to activate" 2>/dev/null
       done) &
       ```
     - When opening new tabs via CDP, always use `background: true` in `new_page` calls
     - **Only bring Chrome to foreground when user interaction is needed** (e.g., login):
       ```bash
       osascript -e 'tell application "Google Chrome" to activate'
       ```
     - After user finishes interaction, hide Chrome again:
       ```bash
       osascript -e 'tell application "System Events" to set visible of process "Google Chrome" to false'
       ```

   - Wait up to 5 seconds, verify with `curl -s http://127.0.0.1:9222/json/version`

   - **Workaround (fragile): Fix MCP DevToolsActivePort detection**: The chrome-devtools MCP reads `DevToolsActivePort` from the **default** Chrome profile path (`~/Library/Application Support/Google/Chrome/`), but when using a custom `--user-data-dir`, Chrome doesn't write it there. Fix by writing it manually:
     ```bash
     # Get the actual websocket endpoint
     WS_PATH=$(curl -s http://127.0.0.1:9222/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['webSocketDebuggerUrl'])")
     BROWSER_PATH=$(echo "$WS_PATH" | sed 's|ws://127.0.0.1:9222||')
     # Write to default location so MCP can find it
     printf '9222\n%s\n' "$BROWSER_PATH" > "$HOME/Library/Application Support/Google/Chrome/DevToolsActivePort"
     ```
   - Retry `list_pages` to confirm CDP connection
   - If still fails, tell user the specific error and ask them to troubleshoot
3. **If connection succeeds**: proceed to Step 1

### Step 1: Verify browser pages & auto-navigate

After confirming CDP connection, use `list_pages` to check available pages.

- **If target site pages are already open**: select and proceed
- **If target site pages are NOT open**: auto-navigate to them
  - Open `https://x.com/home` in a new tab (or navigate an empty tab)
  - Open `https://web.okjike.com/following` in a new tab
  - This ensures login detection (Step 1.5) can run even if user forgot to open the pages

### Step 1.5: Detect login state & handle unauthenticated sessions

After selecting each page, **must check login state before extracting content**. If the user is not logged in, pause and prompt them to log in, then resume.

#### X (Twitter) login detection

1. Take a snapshot after selecting the X page
2. Check for signs of **not logged in**:
   - Page URL is `x.com/i/flow/login` or `x.com/login` or redirected to a login/signup page
   - Snapshot contains "Sign in", "Log in", "Create account", "Sign up" prominently (not inside a post)
   - No `article` role elements in the snapshot (empty timeline)
   - Snapshot contains "Refuse all" / "Accept all" cookie banners blocking content
   - Page shows "Something went wrong" / "Try reloading" → treat as **error**, not login issue. Try reloading the page once.
   - Page shows CAPTCHA or 2FA challenge → bring Chrome to foreground and notify user
   - Page is still loading (snapshot shows only loading shell) → wait 3 seconds and retry snapshot before concluding
   3. If not logged in:
   - **Notify the user** using system notification (see "System Notification" below)
   - **Tell the user in chat**: "❌ X (Twitter) 未登录。请在浏览器中登录你的 X 账户，登录完成后告诉我 'OK' 或 '继续'，我将自动恢复抓取。"
   - **Wait for user confirmation** (the user will reply in chat)
   - After user confirms, re-select the page, re-take snapshot, and verify login state again
   - If still not logged in after retry, skip X and note it in the output: "⚠️ X 未登录，已跳过"

#### 即刻 (Jike) login detection

1. Take a snapshot after selecting the Jike page
2. Check for signs of **not logged in**:
   - Page URL redirects to `web.okjike.com/login` or shows a QR code login page
   - Snapshot contains "扫码登录", "手机号登录", "登录即刻" etc.
   - No post/feed content visible, only login prompts
   - Combine URL check + snapshot + `document.title` for robust detection (don't rely on snapshot text alone)
   3. If not logged in:
   - **Notify the user** using system notification (see "System Notification" below)
   - **Tell the user in chat**: "❌ 即刻未登录。请在浏览器中扫码或手机号登录即刻，登录完成后告诉我 'OK' 或 '继续'，我将自动恢复抓取。"
   - **Wait for user confirmation**
   - After user confirms, re-select the page, re-take snapshot, and verify login state again
   - If still not logged in after retry, skip Jike and note it in the output: "⚠️ 即刻未登录，已跳过"

   #### Notification aggregation

   If **both** sites need login, send **one combined notification** instead of two separate ones:
   - Notification: "X 和即刻均未登录，请在浏览器中登录"
   - Chat message: list both sites in a single message
   - Bring Chrome to foreground once (not twice)

#### System Notification

When the agent needs user attention (login required, task complete, error), split the work into two layers:

1. Generate the short notification text via the user's preferred agent backend when available
2. Deliver the notification with a thin platform adapter

Do not hard-code `osascript` directly in the workflow anymore.

Use [`scripts/run_agent_backend.py`](/Users/bowu/Downloads/news-report/scripts/run_agent_backend.py) to draft the message and [`scripts/send_notification.py`](/Users/bowu/Downloads/news-report/scripts/send_notification.py) to deliver it.

Example:

```bash
cat >/tmp/login-notice.txt <<'EOF'
Write one short desktop notification body in Simplified Chinese.
Scenario: X and Jike both need login.
Requirements:
- under 24 Chinese characters
- imperative tone
- plain text only
EOF

python3 scripts/run_agent_backend.py \
  --backend auto \
  --input /tmp/login-notice.txt \
  --output /tmp/login-notice-body.txt \
  --fallback-text 'X 和即刻都需要登录'

python3 scripts/send_notification.py \
  --title 'News Report' \
  --subtitle '需要登录' \
  --body "$(cat /tmp/login-notice-body.txt)" \
  --sound 'Ping'
```

Use notifications at these points:
- ❌ Any site needs login → subtitle `需要登录`
- ✅ Briefing generation complete → subtitle `任务完成`
- ⚠️ Error that blocks progress → subtitle `需要处理`

If no agent backend is configured, the fallback text is acceptable. The agent is used to improve phrasing and portability, not to gate the workflow.

#### Resume logic & scheduling

The workflow supports **partial completion** and **parallel-first scheduling**:

1. **Batch login check**: In Step 1.5, check login state of **both** sites first before extracting any content
2. **Extract ready sites immediately**: Start extracting from whichever site(s) are logged in — don't wait for the other
3. **Wait only for pending sites**: If one site needs login, extract the ready site while the user logs into the other
4. Track state with:
   - `x_status`: `ready` | `needs_login` | `done` | `skipped`
   - `jike_status`: `ready` | `needs_login` | `done` | `skipped`
5. Only proceed to Step 4 (briefing generation) when both are `done` or `skipped`

> ⚠️ **CDP limitation**: Chrome DevTools MCP operates on one selected page at a time, so snapshot/scroll operations are inherently serial. However, the scheduling ensures no idle waiting — if site A needs login, site B is extracted first, and site A is retried after user confirms login.

### Step 2: Extract X (Twitter) content

Only run when `x_status == ready`. After completion, set `x_status = done`.

1. Select the X page
2. Take an a11y snapshot **only for login detection** (Step 1.5). Once confirmed logged in, switch to `evaluate_script` for content extraction.
3. **Extract via JS** — use `evaluate_script` to query all `article` elements and return a compact JSON array. This avoids the massive a11y tree (nav, sidebar, trending, footer) that wastes thousands of tokens per snapshot. Example extraction script:
   ```js
   () => {
     const posts = [];
     document.querySelectorAll('article').forEach(a => {
       const text = a.innerText;
       // Skip ads
       if (text.includes('广告') || text.includes('Promoted')) return;
       // Extract post URL from timestamp link
       const timeLink = a.querySelector('a[href*="/status/"] time')?.parentElement;
       const url = timeLink?.href || '';
       const time = timeLink?.textContent || '';
       // Extract author
       const authorEl = a.querySelector('[data-testid="User-Name"]');
       const author = authorEl?.textContent || '';
       posts.push({ author, time, url, text: text.substring(0, 500) });
     });
     return JSON.stringify(posts);
   }
   ```
   > The exact selectors may shift as X updates its DOM. If the script returns empty, fall back to a11y snapshot for that round.
4. **Scroll & accumulate**: Use `window.scrollBy(0, 3000)`, wait 2s, then re-run the extraction script. Deduplicate across rounds by post URL. Repeat up to **3 scroll rounds** max. Stop early if a round adds no new posts, or if we encounter `x_last_seen_id` from `scrape-state.json`.
5. After extraction, set `x_status = done`

### Step 3: Extract 即刻 (Jike) content

Only run when `jike_status == ready`. After completion, set `jike_status = done`.

1. Select the Jike page
2. Take an a11y snapshot
3. Parse post items — note Jike's structure is simpler:
   - Author name
   - Post text
   - Likes/comments count
   - Topic/circle link if present
   - Time relative ("11小时前")
4. **Scroll container**: Jike uses a Mantine ScrollArea component. The actual scrollable element is `.mantine-ScrollArea-viewport`, NOT `window`. Using `window.scrollBy()` will NOT trigger lazy loading. You must scroll the viewport element directly:
   ```js
   const viewport = document.querySelector('.mantine-ScrollArea-viewport');
   viewport.scrollTop += viewport.clientHeight * 0.8;
   ```
5. **Scroll & accumulate**: Due to virtualization, the viewport only keeps currently visible posts in DOM. To collect all content, scroll incrementally (step = 80% of clientHeight) and extract `viewport.innerText` at each step, accumulating unique text chunks into a Set. Repeat up to **15 scroll steps**. Stop early if `viewport.scrollTop` stops changing (reached bottom).
6. **Deduplication**: The accumulated text will contain duplicates from overlapping scroll positions. Deduplicate by splitting on double-newlines and using a Set to track seen chunks.
7. After extraction, set `jike_status = done`

### Step 3.5: Handle pending logins

If either site had `needs_login` status and the other has been extracted:
1. Check if user has already confirmed login in chat
2. If yes, re-check login state and extract
3. If no, remind user and wait
4. After all retries, any remaining `needs_login` sites become `skipped`

### Step 4: Generate the briefing

#### Step 4.0: Dedup via last-seen post anchors

Track the newest post seen on each platform to avoid cross-run duplication, even when scraping takes minutes.

**State file**: `data/scrape-state.json`
```json
{
  "x_last_seen_id": "2043852184329105873",
  "jike_last_seen_anchor": "ErinCC|公司在虹桥，从中山公园搬到外环外之后，周中的活动范围都在外环"
}
```

**How it works**:

- **X**: Each post URL contains a numeric status ID (e.g., `https://x.com/user/status/2043852184329105873`). These IDs are **monotonically increasing** — higher = newer. Store the max ID seen. Next run, only include posts with `status_id > x_last_seen_id`.
- **Jike**: No visible post IDs. Construct an anchor from the **first (newest) post**: `"author|first_30_chars_of_content"`. Next run, collect posts until encountering the anchor; skip it and everything below.
- **Fallback**: If `data/scrape-state.json` is missing or unreadable (first run, file deleted), fall back to a **24-hour cutoff** using relative timestamps (`X小时前`, `X天前`, specific dates).

**When to update**: Write the new anchors to `data/scrape-state.json` **after** the briefing is successfully saved, not before — so a failed run doesn't advance the cursor.

#### Step 4.1: Organize and write

Organize extracted content into a structured Markdown briefing:
1. **Group by topic** (AI/tech, startup, life, etc.) rather than by source
2. **Filter noise**: Default to AI/dev/startup/industry topics. Skip pure-life posts (food photos, daily routines, casual chat) unless user explicitly asks for a full personal timeline.
3. **Filter ads**: Remove promoted content
4. **Dedup**: Skip posts already seen in previous runs (see Step 4.0)
5. **Include engagement data**: Helps assess importance
6. **Add source links**: Always include original post URLs
7. **Keep original language**: 引用内容必须保留原文，不做翻译。中文帖保持中文，英文帖保持英文
8. **No summary table**: 不需要在末尾附加统计摘要表格，直接以最后一条内容结束
9. Save output to `output/social-briefing-YYYY-MM-DD.md`
10. **Update state**: Write new anchors to `data/scrape-state.json` (only after step 9 succeeds)

## Key Learnings

### Minimize a11y snapshots — use `evaluate_script` for extraction
A11y snapshots include the **entire page tree** (nav bar, sidebar, trending, footer, compose box, recommended follows…). For X, a single snapshot is 3000–5000 tokens, and we used to take 4 per run (~15K tokens of noise). Now we use a11y snapshots **only for login detection** (one snapshot), then switch to `evaluate_script` with a JS extraction script that returns a compact JSON array of posts (~500 tokens). Same approach for Jike. This cuts extraction token cost by ~90%.

### Jike web: scroll the Mantine viewport, not window
Jike's web version uses a Mantine ScrollArea component. The scrollable container is `.mantine-ScrollArea-viewport`, NOT `window` or `document.body`. Using `window.scrollBy()` does nothing — you must scroll the viewport element directly. Due to virtualization, only visible posts remain in DOM, so you must accumulate content incrementally at each scroll step. This approach successfully loads 20+ posts (previously only 3 were captured).

### Content quality varies widely
Social timelines contain a mix of valuable insights and casual posts. Effective filtering requires either:
- LLM-based relevance scoring
- User-configured topic filters
- Engagement threshold (e.g., only posts with >10 likes)

### 保留原文，不翻译引用
帖子内容必须原文呈现。中文帖保持中文，英文帖保持英文。不对引用内容做任何翻译或改写，只在必要时用简短的中文标注提供上下文。

### 不需要简报总结表
不要在末尾加统计表格（来源数、条目数等），直接以最后一条内容结束即可。

## Output Format

```markdown
# 社交媒体要闻简报 — YYYY-MM-DD

> 来源：X (Twitter) 关注时间线 + 即刻关注动态

---

## 🔥 Topic Category

### 1. Post Title / First Line
**@author** · time
原文内容（保持原始语言，不翻译）
- 🔗 [原帖](url)
- 📊 Engagement metrics

（以最后一条内容结束，不加总结表格）
```

## Integration with news-report project

This skill produces output compatible with the news-report briefing format. The `cdp_browser.py` adapter in `news_report/adapters/` contains normalization functions that can convert raw scraped data into the `SourceAdapter` candidate format used by `generate_briefing()`.

## Cross-platform compatibility

This skill is currently **macOS only** (tested on macOS + Chrome 146). Linux and Windows notes below are **unverified porting references**.

| Area | macOS (current ✅) | Windows | Linux |
|------|-------------------|---------|-------|
| Chrome binary path | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` | `C:\Program Files\Google\Chrome\Application\chrome.exe` | `google-chrome` or `chromium-browser` |
| DevToolsActivePort | `~/Library/Application Support/Google/Chrome/DevToolsActivePort` | `%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort` | `~/.config/google-chrome/DevToolsActivePort` |
| Debug profile dir | `~/.chrome-debug-profile` | `%USERPROFILE%\.chrome-debug-profile` | `~/.chrome-debug-profile` |
| Suppress debug dialog | `defaults write com.google.Chrome DevToolsRemoteDebuggingAllowed -bool true` | Registry: `HKLM\SOFTWARE\Policies\Google\Chrome\DevToolsRemoteDebuggingAllowed = 1` | `/etc/opt/chrome/policies/managed/devtools.json` |
| Hide Chrome window | `osascript` (AppleScript) | PowerShell: `$w = Get-Process chrome; $w.MainWindowHandle` + `ShowWindow($handle, 0)` | `xdotool windowminimize` |
| Refocus prev app | `osascript -e 'tell app to activate'` | PowerShell: `[Win32]::SetForegroundWindow($handle)` | `xdotool windowactivate` |
| System notification | `osascript -e 'display notification ...'` | PowerShell: `New-BurntToastNotification` or `[Windows.UI.Notifications]` | `notify-send "title" "body"` |
| Cookie encryption | Keychain-bound, profile copy does NOT work | DPAPI-bound, profile copy within same user MAY work | Secret Service/kwallet, profile copy MAY work |
| `--user-data-dir` req (Chrome 136+) | Required ✅ | Likely required — needs testing | Likely required — needs testing |

### Porting priority

1. **Linux** — easiest. Most commands have direct equivalents, Chrome policy via JSON file, `notify-send` for notifications, `xdotool` for window management
2. **Windows** — moderate. Needs PowerShell for window hiding/notifications, Registry for policy, different path conventions

### How to detect OS in the workflow

```bash
OS=$(uname -s)
case "$OS" in
  Darwin) echo "macOS" ;;
  Linux)  echo "Linux" ;;
  MINGW*|MSYS*|CYGWIN*) echo "Windows" ;;
esac
```

Use this at the start of Step 0 to branch into platform-specific logic.

## 使用须知

- 仅在用户自己的账户、自己已打开的页面上进行只读提取
- 遵守各平台的使用条款（Terms of Service）
- 不自动导航到未授权页面，不执行写入操作
- 输出文件可能包含个人社交上下文，`output/` 已加入 `.gitignore`，不应提交到公开仓库
