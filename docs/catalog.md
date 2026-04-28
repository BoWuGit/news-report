# Resource Catalog

This file is generated from `data/sources.json` by `scripts/build_catalog.py`.

## agent_tool

### baoyu-youtube-transcript

- id: `baoyu-youtube-transcript`
- url: https://github.com/jimliu/baoyu-skills
- interfaces: `cli`, `skills`
- content types: `transcript`, `video`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: Download YouTube video transcripts/subtitles with multi-language, chapters, and speaker identification support.
- note: Part of baoyu-skills. Supports caching, SRT output, and translation.
- note: Useful for turning video content into structured text for briefing generation.

### Cubox CLI

- id: `cubox-cli`
- url: https://help.cubox.pro/ai/agents
- interfaces: `cli`, `skills`, `api`
- content types: `article`, `highlight`, `note`, `read_later`
- open source: `no`
- agent friendly: `high`
- pricing: `mixed`
- stage: `active`
- summary: Official Cubox command-line interface that lets AI agents read, search, collect, and organize a user's private reading library.
- note: Strong reference for private read-later libraries becoming agent-callable information sources.
- note: Useful benchmark for search, highlights, Markdown content retrieval, and cross-tool workflows.

### MarsWave Skills

- id: `marswave-skills`
- url: https://github.com/marswaveai/skills
- interfaces: `cli`, `skills`
- content types: `podcast`, `article`, `transcript`, `summary`
- open source: `yes`
- agent friendly: `high`
- pricing: `mixed`
- stage: `active`
- summary: Collection of AI agent skills for content creation: podcast, explainer video, slides, TTS, content parsing, and multi-skill orchestration.
- note: Skill-per-directory architecture with structured SKILL.md specs is a good reference for skill design.
- note: content-parser and creator orchestration patterns relevant to briefing generation pipelines.

### Matter CLI

- id: `matter-cli`
- url: https://docs.getmatter.com/cli
- interfaces: `cli`
- content types: `article`, `highlight`, `annotation`
- open source: `no`
- agent friendly: `medium`
- pricing: `paid`
- stage: `active`
- summary: Terminal client for Matter reading libraries with scriptable CLI commands and an interactive TUI.

### Podwise CLI

- id: `podwise-cli`
- url: https://github.com/hardhackerlabs/podwise-cli
- interfaces: `cli`, `mcp`, `skills`
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
- content types: `article`, `highlight`
- open source: `no`
- agent friendly: `medium`
- pricing: `paid`
- stage: `active`
- summary: CLI access to saved reading data that can be composed into agent workflows.
- note: Strong bridge between personal knowledge workflows and agent automation.
- note: Depends on the user's upstream Readwise usage.

### TransCrab

- id: `transcrab`
- url: https://github.com/onevcat/transcrab
- interfaces: `cli`, `skills`
- content types: `article`, `translation`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: OpenClaw-first translation pipeline, turns a link into a polished translated reading page.
- note: Fetch → extract → translate → deploy as static site.
- note: Good reference for content transformation and agent-driven publishing.

### YouTube Transcript API

- id: `youtube-transcript`
- url: https://github.com/jdepoix/youtube-transcript-api
- interfaces: `api`, `cli`
- content types: `transcript`, `summary`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: Python API to fetch YouTube video transcripts without an API key.
- note: Enables turning video content into text for briefing generation.

## open_source_project

### arXiv RSS Feeds

- id: `arxiv-rss`
- url: https://arxiv.org/
- interfaces: `rss`
- content types: `article`, `feed`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: Academic preprint RSS feeds covering AI, ML, NLP, and more.
- note: Key source for cutting-edge AI/ML research. Available via RSSHub /arxiv/ routes.

### GitHub Trending

- id: `github-trending`
- url: https://github.com/trending
- interfaces: `rss`, `web`
- content types: `feed`, `article`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: GitHub trending repositories. Accessible via RSSHub route /github/trending/daily.
- note: Useful for open-source and developer-tools topics.

### Hacker News API

- id: `hackernews-api`
- url: https://github.com/HackerNews/API
- interfaces: `api`
- content types: `article`, `feed`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: Official Hacker News Firebase API. Free, no auth, returns structured JSON.
- note: Good candidate for second real adapter to validate SourceAdapter Protocol.

### Lobsters

- id: `lobsters`
- url: https://lobste.rs/
- interfaces: `rss`, `web`
- content types: `article`, `feed`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: Technology-focused link aggregation with tag-based RSS feeds.
- note: High signal-to-noise ratio. Tag-based RSS enables topic-specific feeds.

### Reddit RSS Feeds

- id: `reddit-rss`
- url: https://www.reddit.com/r/{subreddit}/.rss
- interfaces: `rss`, `api`
- content types: `article`, `feed`
- open source: `no`
- agent friendly: `medium`
- pricing: `free`
- stage: `active`
- summary: Reddit subreddit RSS feeds. Accessible via RSSHub /reddit/subreddit/ routes.
- note: Useful for niche topic monitoring. Rate-limited but functional via RSSHub.

### RSSHub

- id: `rsshub`
- url: https://github.com/DIYgod/RSSHub
- interfaces: `rss`, `web`
- content types: `feed`, `article`
- open source: `yes`
- agent friendly: `high`
- pricing: `free`
- stage: `active`
- summary: Open source feed generation infrastructure that turns many web sources into RSS.
- note: Important upstream building block for source normalization.
- note: Relevant as infrastructure rather than a briefing product.

## processing_tool

### Kill the Newsletter!

- id: `kill-the-newsletter`
- url: https://kill-the-newsletter.com/
- interfaces: `rss`, `email`
- content types: `article`, `feed`
- open source: `yes`
- agent friendly: `medium`
- pricing: `free`
- stage: `active`
- summary: Converts email newsletters into RSS feeds for agent consumption.
- note: Bridges the gap between newsletter-only content and structured feeds.

### n8n RSS Trigger

- id: `n8n-rss`
- url: https://n8n.io/
- interfaces: `api`, `web`
- content types: `feed`, `article`
- open source: `yes`
- agent friendly: `medium`
- pricing: `mixed`
- stage: `active`
- summary: Workflow automation with RSS trigger nodes for feed processing pipelines.
- note: Can orchestrate multi-source feed processing. Self-hostable.

## saas_source_service

### Feedly API

- id: `feedly-api`
- url: https://developer.feedly.com/
- interfaces: `api`, `web`
- content types: `feed`, `article`
- open source: `no`
- agent friendly: `medium`
- pricing: `paid`
- stage: `active`
- summary: RSS aggregator with AI-powered topic tracking and REST API.
- note: Leo AI feature does topic filtering. API requires paid plan.

### Inoreader Intelligence Reports

- id: `inoreader-intelligence-reports`
- url: https://www.inoreader.com/blog/2026/03/automated-intelligence-reports-for-insights-delivered-to-you.html
- interfaces: `web`
- content types: `feed`, `article`
- open source: `no`
- agent friendly: `low`
- pricing: `paid`
- stage: `active`
- summary: RSS reading product with automated intelligence reporting features.
- note: Useful as a benchmark for reporting UX and scheduled briefing workflows.
- note: Not an agent-first or open integration surface yet.

### Techmeme

- id: `techmeme`
- url: https://www.techmeme.com/
- interfaces: `rss`, `web`
- content types: `article`, `feed`
- open source: `no`
- agent friendly: `medium`
- pricing: `free`
- stage: `active`
- summary: Curated tech news aggregator with RSS feed.
- note: High-quality editorial curation. RSS feed provides structured access.

### TLDR Newsletter

- id: `tldr-newsletter`
- url: https://tldr.tech/
- interfaces: `web`, `email`
- content types: `article`, `feed`
- open source: `no`
- agent friendly: `low`
- pricing: `free`
- stage: `active`
- summary: Daily tech newsletter covering AI, startups, and developer tools.
- note: Good curation quality. Can be converted to RSS via Kill the Newsletter.
