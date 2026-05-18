# News Report For User Agent

**English** · [简体中文](./README.zh-CN.md)

> Agent-native briefing compiler — turn messy, multi-source information streams into verifiable, personalized, machine-readable briefings.

As personal AI assistants (such as [OpenClaw](https://github.com/openclaw/openclaw)) mature, user agents increasingly need structured, callable, and auditable information retrieval. **News Report** is an agent-native briefing compiler: it helps AI assistants discover quality sources, normalize and enrich content, and generate briefings that can be consumed through CLI, MCP, schemas, and other agent-facing interfaces.

## Positioning

```text
User agent
        |
        v
News Report (agent-native briefing compiler)
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
- **Agent-native by default**: outputs are structured, explainable, and designed for user agents to call, verify, and reuse

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
| [Cubox CLI](https://help.cubox.pro/ai/agents) | Official Cubox CLI for agent access to private reading libraries, highlights, search, and organization workflows |
| [TransCrab](https://github.com/onevcat/transcrab) | OpenClaw-first translation pipeline turning links into polished reading pages |
| [baoyu-youtube-transcript](https://github.com/jimliu/baoyu-skills) | YouTube transcript download with multilingual, chapter, and speaker support |
| [RSSHub](https://github.com/DIYgod/RSSHub) | “Everything can be RSS” — 42k+ stars |
| [bb-browser](https://github.com/epiral/bb-browser) | AI browser that reuses real login sessions for sources that require auth (e.g. Twitter, Xiaohongshu); local browsing-history recommendations are also worth a look |

See the full catalog in [docs/catalog.md](docs/catalog.md) and raw data in [data/sources.json](data/sources.json).

## Quick start

Build the resource catalog:

```bash
uv run news-report catalog build
```

Generate a local briefing prototype:

```bash
uv run news-report briefing generate examples/briefing-request.json
```

Read request JSON from stdin:

```bash
cat examples/briefing-request.json | uv run news-report briefing generate - --format markdown
```

Inspect agent-facing metadata:

```bash
uv run news-report sources list --json
uv run news-report sources get rsshub --json
uv run news-report schemas get briefing-request
uv run news-report doctor --skip-network
```

Backward-compatible entry points remain available:

```bash
uv run build-catalog
uv run generate-briefing examples/briefing-request.json
uv run news-report-mcp
```

Run tests:

```bash
uv run pytest
```

### Publish a briefing to Notion with `ntn`

If you use the [Notion CLI](https://developers.notion.com/cli/get-started/overview), generate Markdown and pipe it into a Notion page:

```bash
uv run news-report briefing generate examples/briefing-request.json --format markdown \
  | ntn pages create --parent page:$NOTION_PAGE_ID
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
- [Cubox CLI - 唤醒你沉睡的阅读宝藏](https://mp.weixin.qq.com/s/5FF4lthSEBKNDSzOZcpIfg) — product case for making private reading memory callable by agents
- [Karpathy: LLM Knowledge Bases](https://x.com/karpathy/status/2039805659525644595) — end-to-end workflow for personal knowledge bases with LLMs, closely aligned with this project
- Thanks to [One2X](https://one2x.ai) Guange for product thinking that inspired the direction

## License

MIT
