# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0.0] - 2026-03-31

### Added
- **Adapter Protocol**: `SourceAdapter` Protocol with `fetch()` and `ping()` methods, enabling pluggable data source adapters
- **RSSHub real adapter**: First real adapter that fetches live RSS data from RSSHub instances, with topic-to-route mapping and graceful error handling
- **Adapter registry**: Auto-selects real adapters when available, falls back to mock for sources without adapters
- **JSON Schema validation**: Request and source validation using `jsonschema` library against existing schema files, replacing hand-written validation
- **Briefing cache**: File-based caching with SHA256 request hashing, 15-minute TTL, and automatic corruption recovery
- **Markdown output**: `--format markdown` CLI flag for human-readable briefing output
- **Source health check**: `--check-sources` CLI flag to ping all source adapters and report availability
- **CLI enhancements**: `--verbose` for debug logging, `--no-cache` to bypass cache
- **12 new sources**: Expanded catalog from 4 to 16 entries including Hacker News API, GitHub Trending, arXiv RSS, Lobsters, Miniflux, YouTube Transcript API, and more
- **27 new tests**: Coverage for adapter protocol, RSSHub (mock HTTP), cache TTL/corruption, Markdown formatter, and schema validation

### Changed
- Moved mock adapter from `mock_adapters.py` to `news_report/adapters/mock.py` as part of the adapter package
- `briefing.py` now imports from `news_report.adapters` instead of `news_report.mock_adapters`
- Added `httpx`, `feedparser`, and `jsonschema` as runtime dependencies

### Removed
- `news_report/mock_adapters.py` (replaced by `news_report/adapters/mock.py`)
