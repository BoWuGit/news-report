# social-timeline-runtime

This package is the future standalone runtime for the `scraping-social-timeline`
skill.

It exists in this repository first so the team can stabilize the contract before
splitting repositories or publishing to `skills.sh`.

## Scope

- browser/login orchestration
- timeline extraction
- candidate normalization
- notifications
- agent-backend bridge
- CLI contract used by the published skill

## Current State

Some modules still delegate to `news_report` implementations for normalization
and notifications. That is an intentional bridge during migration, not the final
ownership model.

## CLI

```bash
social-timeline check-login --site x
social-timeline scrape --site x --output raw.json
social-timeline normalize --site x --input raw.json --output candidates.json
social-timeline notify --title "Need login" --body "Please sign in to X"
social-timeline run-agent --input prompt.txt --output result.md
```

The browser-facing commands connect to Chrome's remote debugging endpoint, which
defaults to `http://127.0.0.1:9222` and can be overridden with `--chrome-url`.
