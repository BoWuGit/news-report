# Resource Catalog

This file is generated from `data/sources.json` by `scripts/build_catalog.py`.

## agent_tool

### Podwise CLI

- id: `podwise-cli`
- url: https://github.com/hardhackerlabs/podwise-cli
- interfaces: `cli`, `mcp`
- content types: `podcast`, `transcript`, `summary`
- open source: `yes`
- agent friendly: `high`
- pricing: `mixed`
- stage: `active`
- summary: Podcast summarization and transcript workflow with CLI and MCP support.
- note: A strong example of vertical tool design for agent consumption.
- note: Good reference for how News Report can expose structured outputs.

### Readwise CLI

- id: `readwise-cli`
- url: https://x.com/readwise/status/2034302848805241282
- interfaces: `cli`
- content types: `article`, `highlight`, `read_later`
- open source: `no`
- agent friendly: `medium`
- pricing: `paid`
- stage: `active`
- summary: CLI access to saved reading data that can be composed into agent workflows.
- note: Strong bridge between personal knowledge workflows and agent automation.
- note: Depends on the user's upstream Readwise usage.

## saas_source_service

### Inoreader Intelligence Reports

- id: `inoreader-intelligence-reports`
- url: https://www.inoreader.com/blog/2026/03/automated-intelligence-reports-for-insights-delivered-to-you.html
- interfaces: `web`
- content types: `rss`, `article`
- open source: `no`
- agent friendly: `low`
- pricing: `paid`
- stage: `active`
- summary: RSS reading product with automated intelligence reporting features.
- note: Useful as a benchmark for reporting UX and scheduled briefing workflows.
- note: Not an agent-first or open integration surface yet.
