---
name: scraping-social-timeline
description: "Scrapes authenticated social media timelines (X/Twitter, Jike) via Chrome DevTools Protocol and generates a structured briefing."
---

# Scraping Social Media Timelines

This is the publishable skill surface. It must stay decoupled from project-local
modules and scripts.

## Runtime Contract

This skill depends on the `social-timeline` CLI from the
`social-timeline-runtime` package.

Required commands:

```bash
social-timeline check-login --site x
social-timeline scrape --site x --output /tmp/x-raw.json --max-items 3
social-timeline normalize --site x --input /tmp/x-raw.json --output /tmp/x-candidates.json --source-id x-timeline --source-name "X (Twitter)"
social-timeline notify --title "Login required" --body "Please sign in to X"
social-timeline run-agent --input /tmp/prompt.txt --output /tmp/result.md
```

## Rules

- Keep workflow instructions here.
- Do not reference `news_report.*`.
- Do not reference repository-private script paths.
- Prefer the runtime CLI even when the same logic exists elsewhere in a host app.

## Workflow

1. Verify CDP/browser availability.
2. Open or select the target social page.
3. Check login state.
4. If login is required, notify the user and pause.
5. Scrape raw timeline items.
6. For smoke tests or low-cost checks, pass `--max-items 3`.
7. Normalize raw items into candidate objects.
8. Summarize or hand off to the host application.

## Notes For Maintainers

If a new site is added, update the runtime package first and then extend this
skill only where the user-facing workflow changes.
