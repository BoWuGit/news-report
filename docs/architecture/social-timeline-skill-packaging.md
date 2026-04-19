# Social Timeline Skill Packaging

This document defines the repository boundary for the social timeline briefing skill.

## Goal

Keep three concerns separate so the skill can be published to `skills.sh` without
dragging the whole `news-report` application with it.

1. Skill layer
   Contains the published `SKILL.md`, user-facing setup instructions, and minimal
   MCP configuration.
2. Runtime layer
   Contains the executable code that the skill calls through a stable CLI/API.
3. App layer
   Contains `news-report` integration code that consumes runtime outputs and feeds
   them into the local briefing pipeline.

## Repository Rule

The skill must never depend on `news_report.*` imports or project-private script
paths. It should depend only on the runtime CLI contract.

Today this repository still contains bridge imports while the runtime is being
extracted. Those bridges are acceptable only inside the runtime package, not in
the published skill.

## Target Layout

```text
skills/scraping-social-timeline/
  SKILL.md
  README.md
  mcp.json

packages/social_timeline_runtime/
  pyproject.toml
  README.md
  src/social_timeline_runtime/

news_report/
  adapters/
  briefing.py
```

## Stable Runtime Contract

The runtime is expected to provide these commands:

```bash
social-timeline check-login --site x
social-timeline scrape --site x --output raw.json
social-timeline normalize --site x --input raw.json --output candidates.json
social-timeline notify --title "..." --body "..."
social-timeline run-agent --input prompt.txt --output result.md
```

The CLI surface is the compatibility boundary. Internal module names may change,
but these commands should remain stable across minor releases.

## Migration Policy

Phase 1: Monorepo bridge
- Runtime package may temporarily reuse existing `news_report` modules.
- Existing in-repo skill under `.agents/skills/` keeps working.

Phase 2: Runtime ownership
- Browser extraction, normalization, notifications, and agent backend runner live
  inside `packages/social_timeline_runtime`.
- `news-report` consumes the runtime package instead of owning those pieces.

Phase 3: External publishing
- Publish the skill directory to `skills.sh`.
- If release cadence or contributor surface diverges, split the runtime into its
  own repository.

## Maintenance Rules

- Add new social-site support in the runtime package first.
- Keep skill docs workflow-oriented; do not leak project-private implementation.
- Test runtime behavior with unit tests and one CLI smoke test.
- Version the runtime independently once it is consumed outside this repository.
