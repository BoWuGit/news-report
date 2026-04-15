---
name: scraping-social-timeline
description: "Scrapes authenticated social media timelines (X/Twitter, Jike) and generates a structured briefing."
---

# Scraping Social Media Timelines

This in-repo skill is a thin wrapper over the publishable skill in
`skills/scraping-social-timeline/SKILL.md`. Keep workflow changes there first.

## Prerequisites

- The user is logged into X and Jike inside the dedicated Chrome profile
  (`~/.news-report/chrome-profile`). First-time setup requires one manual login;
  sessions persist across runs.
- Use `uv run` to execute commands (ensures correct venv and workspace deps).

## Workflow

1. **Always use the runtime CLI** — do NOT scrape via MCP snapshots or manual
   browser interaction. The runtime auto-launches Chrome with a dedicated
   `--user-data-dir` profile, so no manual Chrome setup is needed.
2. Run `check-login` → if exit code `2`, notify the user to log in once.
3. Run `scrape` for each site → raw JSON.
4. Run `normalize` → candidate JSON.
5. Hand off candidates to the agent for briefing generation.

## Runtime Commands

```bash
uv run social-timeline check-login --site x
uv run social-timeline scrape --site x --output /tmp/x-raw.json
uv run social-timeline scrape --site jike --output /tmp/jike-raw.json
uv run social-timeline normalize --site x --input /tmp/x-raw.json --output /tmp/x-candidates.json --source-id x-timeline --source-name "X (Twitter)"
uv run social-timeline normalize --site jike --input /tmp/jike-raw.json --output /tmp/jike-candidates.json --source-id jike-following --source-name "即刻"
uv run social-timeline notify --title "News Report" --body "需要登录"
```

## Briefing Rules

- **Do NOT translate** original post text. Keep English posts in English, Chinese
  posts in Chinese. The briefing summary/commentary can be in `zh-CN` but quoted
  content must stay in its original language.
- **No summary table** — do NOT append a statistics/summary table at the end.
  End the briefing after the last content item.

## Scrape State (`data/scrape-state.json`)

Tracks the last-seen cursor so successive runs skip already-reported content.

```json
{
  "x_last_seen_id": "2044045951279808885",
  "jike_last_seen_anchor": "Lightory|现在把播客分为三类"
}
```

- **X**: Post URLs contain monotonically increasing status IDs. Store the max ID
  seen; next run only includes posts with a higher ID.
- **Jike**: No visible post IDs. Anchor = `"author|first_30_chars"` of the newest
  post. Next run collects posts until hitting the anchor.
- **Fallback**: If the file is missing (first run), use a 24-hour cutoff based on
  relative timestamps.
- **Write timing**: Update `scrape-state.json` only **after** the briefing file is
  successfully saved.

## Notes

- Source of truth for workflow and packaging rules: `skills/scraping-social-timeline/SKILL.md`
- `check-login` exits `0` when logged in, `2` when login is required, and `1` on runtime errors.
- `scrape` returns raw site-shaped JSON; `normalize` converts it to the candidate schema used by `news-report`.
- Use `--max-items 3` for local smoke tests and low-cost validation.
- Chrome auto-launch uses `ensure_chrome()` from `browser.py` — it finds the
  Chrome binary, starts it with `--remote-debugging-port=9222` and a dedicated
  `--user-data-dir`, and waits for the debug port to respond.
