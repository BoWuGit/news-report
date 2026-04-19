# News Report For User Agent

**English** · [简体中文](./README.zh-CN.md)

> News briefings for user agents — help AI assistants deliver personalized information efficiently.

As personal AI assistants (such as [OpenClaw](https://github.com/openclaw/openclaw)) mature, user agents increasingly need structured information retrieval. **News Report** aims to be an [RSSHub](https://rsshub.app/)-style layer for agents — tools and services that help AI assistants discover quality sources, normalize and enrich content, and generate personalized briefings.

## Positioning

```text
User agent
        |
        v
News Report (information middleware)
- source registry
- normalization
- enrichment
- briefing generation
        |
        v
RSS / API / Newsletter / Podcast / Social / Read-later
```

- **No user profiling**: users can supply preferences to News Report and receive personalized results through computation alone
- **No fixed taxonomy**: focused on reusable processing primitives rather than a single content vertical
- **Does not author primary content**: aggregates, transforms, and summarizes existing material

## Project phases

### Phase 1: Resource collection & community (current)

Curate existing and emerging services and tools, organize them for sharing, and learn what people want.

This repository already includes three foundational layers:

- `data/`: structured inventories of resources
- `schemas/`: reusable data models for Phase 1 and later MVP work
- `docs/`: roadmap, MVP specs, open questions, and an auto-generated catalog

### Phase 2: Tooling & integration

Design and build agent-facing information tools:

- Source discovery and aggregation
- Content processing and transformation (summarize, translate, format)
- Briefing generation

### Phase 3: Service deployment

- Open-source deployment with public access to quality content
- On-demand personalized deployments (similar in spirit to Hugging Face model hosting)
- Shared deployments to split costs across groups

## Ecosystem resources

### SaaS source services

| Service | Notes |
|---------|-------|
| [Inoreader Intelligence Reports](https://www.inoreader.com/blog/2026/03/automated-intelligence-reports-for-insights-delivered-to-you.html) | RSS reader with automated intelligence reports |
| [Readwise CLI](https://x.com/readwise/status/2034302848805241282) | CLI for highlights and articles with agent integration |

### [Agent Skills](https://agentskills.io) / CLI tools

| Tool | Notes |
|------|-------|
| [Podwise CLI](https://github.com/hardhackerlabs/podwise-cli) | Podcast transcription & summarization with MCP server and [Agent Skills](https://agentskills.io) |
| [TransCrab](https://github.com/onevcat/transcrab) | OpenClaw-first translation pipeline turning links into polished reading pages |
| [baoyu-youtube-transcript](https://github.com/jimliu/baoyu-skills) | YouTube transcript download with multilingual, chapter, and speaker support |
| [RSSHub](https://github.com/DIYgod/RSSHub) | “Everything can be RSS” — 42k+ stars |
| [bb-browser](https://github.com/epiral/bb-browser) | AI browser that reuses real login sessions for sources that require auth (e.g. Twitter, Xiaohongshu); local browsing-history recommendations are also worth a look |

See the full catalog in [docs/catalog.md](docs/catalog.md) and raw data in [data/sources.json](data/sources.json).

## Quick start

Build the resource catalog:

```bash
uv run scripts/build_catalog.py
```

Generate a local briefing prototype:

```bash
uv run scripts/generate_briefing.py examples/briefing-request.json
```

Run tests:

```bash
uv run pytest
```

## Skill packaging boundary

Social timeline briefing is being shaped into a publishable skill plus a standalone runtime:

- Published skill scaffold: [skills/scraping-social-timeline/SKILL.md](skills/scraping-social-timeline/SKILL.md)
- Runtime package scaffold: [packages/social_timeline_runtime/README.md](packages/social_timeline_runtime/README.md)
- Architecture notes: [docs/architecture/social-timeline-skill-packaging.md](docs/architecture/social-timeline-skill-packaging.md)

Existing `.agents/skills/` integrations remain until the runtime CLI migration stabilizes.

## Assumptions & prerequisites


- User memory in the AI ecosystem will keep maturing
  - Whether local-first stacks like [OpenClaw](https://github.com/openclaw/openclaw) or large “super apps”
  - Challenges remain (e.g. [Karpathy on memory interference](https://x.com/karpathy/status/2036836816654147718))
- Agents must help with information overload — summarization and synthesis are strengths of LLMs

## References

- Earlier essay: [阅读产品在AI时代的想象力](https://mp.weixin.qq.com/s/sSP9j-qLZQBJiyLSrCYzWQ) (Chinese)
- [Karpathy: LLM Knowledge Bases](https://x.com/karpathy/status/2039805659525644595) — end-to-end workflow for personal knowledge bases with LLMs, closely aligned with this project
- Thanks to [One2X](https://one2x.ai) Guange for product thinking that inspired the direction

## License

MIT
