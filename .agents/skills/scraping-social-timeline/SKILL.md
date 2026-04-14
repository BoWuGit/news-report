---
name: scraping-social-timeline
description: "Scrapes authenticated social media timelines (X/Twitter, Jike) and generates a structured briefing."
---

# Scraping Social Media Timelines

This in-repo skill is a thin wrapper over the publishable skill in
`skills/scraping-social-timeline/SKILL.md`. Keep workflow changes there first.

## Prerequisites

- Chrome is running with remote debugging enabled on `http://127.0.0.1:9222`
- The user is logged into the target site inside that Chrome profile
- The runtime CLI is available via:

```bash
PYTHONPATH=packages/social_timeline_runtime/src python3 -m social_timeline_runtime.cli --help
```

## Runtime Commands

```bash
PYTHONPATH=packages/social_timeline_runtime/src python3 -m social_timeline_runtime.cli check-login --site x
PYTHONPATH=packages/social_timeline_runtime/src python3 -m social_timeline_runtime.cli scrape --site x --output /tmp/x-raw.json --max-items 3
PYTHONPATH=packages/social_timeline_runtime/src python3 -m social_timeline_runtime.cli normalize --site x --input /tmp/x-raw.json --output /tmp/x-candidates.json --source-id x-timeline --source-name "X (Twitter)"
PYTHONPATH=packages/social_timeline_runtime/src python3 -m social_timeline_runtime.cli run-agent --input /tmp/prompt.txt --output /tmp/result.md
PYTHONPATH=packages/social_timeline_runtime/src python3 -m social_timeline_runtime.cli notify --title "News Report" --body "需要登录"
```

## Notes

- Source of truth for workflow and packaging rules: `skills/scraping-social-timeline/SKILL.md`
- `check-login` exits `0` when logged in, `2` when login is required, and `1` on runtime errors.
- `scrape` returns raw site-shaped JSON; `normalize` converts it to the candidate schema used by `news-report`.
- Use `--max-items 3` for local smoke tests and low-cost validation.
