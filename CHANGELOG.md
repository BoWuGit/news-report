# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0.0] - 2026-04-03

### Added
- **MCP Server**: Briefing pipeline exposed as MCP tools (`generate_briefing`, `list_sources`, `check_source_health`) and resources (sources catalog, request schema) via FastMCP, with `news-report-mcp` entry point for stdio transport
- **8 MCP tests**: Coverage for all tools and resources

### Fixed
- `list_sources_tool` now returns `summary` field (was incorrectly referencing `description`)
- `check_source_health_tool` gracefully handles missing adapters instead of crashing
- Path resolution for `data/` and `schemas/` now works both from repo checkout and pip install

### Changed
- `catalog.py`, `briefing.py`, `mcp_server.py` use unified `_resolve_dir()` for path resolution
- `pyproject.toml` includes `data/` and `schemas/` in wheel via hatchling `force-include`

## [0.2.0.0] - 2026-03-31

### Added
- **Adapter Protocol**: `SourceAdapter` Protocol with `fetch()` and `ping()` methods, enabling pluggable data source adapters
- **RSSHub real adapter**: First real adapter that fetches live RSS data from RSSHub instances, with topic-to-route mapping and graceful error handling
- **Adapter registry**: Auto-selects real adapters when available, falls back to mock for sources without adapters
- **JSON Schema validation**: Request and source validation using `jsonschema` library against existing schema files, replacing hand-written validation
- **Markdown output**: `--format markdown` CLI flag for human-readable briefing output
- **Source health check**: `--check-sources` CLI flag to ping all source adapters and report availability
- **CLI enhancements**: `--verbose` for debug logging
- **12 new sources**: Expanded catalog from 4 to 16 entries including Hacker News API, GitHub Trending, arXiv RSS, Lobsters, YouTube Transcript API, and more
- **27 new tests**: Coverage for adapter protocol, RSSHub (mock HTTP), Markdown formatter, and schema validation

### Changed
- Moved mock adapter from `mock_adapters.py` to `news_report/adapters/mock.py` as part of the adapter package
- `briefing.py` now imports from `news_report.adapters` instead of `news_report.mock_adapters`
- Added `httpx`, `feedparser`, and `jsonschema` as runtime dependencies

### Removed
- `news_report/mock_adapters.py` (replaced by `news_report/adapters/mock.py`)
