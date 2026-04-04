"""News Report MCP Server — exposes briefing pipeline as MCP tools and resources."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from news_report.briefing import generate_briefing, validate_request
from news_report.catalog import load_sources, validate_sources
from news_report.formatter import format_briefing_markdown
from news_report.paths import resolve_package_adjacent_dir

logger = logging.getLogger(__name__)

# Default when *sources* is omitted: fast, mostly mock adapters — avoids N×M network fetches.
DEFAULT_MCP_BRIEFING_SOURCES: tuple[str, ...] = (
    "podwise-cli",
    "readwise-cli",
    "inoreader-intelligence-reports",
)

mcp = FastMCP(
    "news-report",
    instructions=("面向用户 Agent 的新闻简报工具。提供信息源发现、健康检查和个性化简报生成。"),
)


_DATA_DIR = resolve_package_adjacent_dir("data")
_SCHEMAS_DIR = resolve_package_adjacent_dir("schemas")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def generate_briefing_tool(
    topics: list[str],
    sources: list[str] | None = None,
    language: str = "zh-CN",
    max_items: int = 10,
    summary_style: str = "concise",
    explicit_preferences: list[str] | None = None,
    blocked_topics: list[str] | None = None,
    time_decay_days: int = 30,
    diversity_floor: float = 0.2,
    output_format: str = "json",
) -> str:
    """生成个性化新闻简报。

    根据用户指定的主题、信息源和偏好，从多个数据源抓取内容，
    经过评分、排序和去重后，返回结构化的简报。

    Args:
        topics: 感兴趣的主题列表，如 ["AI", "open source"]
        sources: 要查询的信息源 ID 列表。传 None 则使用少量默认源（本地/mock 为主，避免隐式全量外呼）。
        language: 输出语言，默认 zh-CN
        max_items: 最多返回条目数，默认 10
        summary_style: 摘要风格 (headline_only / concise / detailed)
        explicit_preferences: 显式偏好关键词，如 ["agent tools", "developer workflows"]
        blocked_topics: 需要屏蔽的主题
        time_decay_days: 时效衰减天数，默认 30
        diversity_floor: 多样性下限 (0-1)，默认 0.2
        output_format: 输出格式，仅支持 json 或 markdown（大小写不敏感）

    Returns:
        简报内容（JSON 字符串或 Markdown）
    """
    all_sources = validate_sources(load_sources())

    if sources is None:
        sources = list(DEFAULT_MCP_BRIEFING_SOURCES)

    fmt = (output_format or "json").strip().lower()
    if fmt not in {"json", "markdown"}:
        raise ValueError("output_format must be 'json' or 'markdown'")

    request: dict[str, Any] = {
        "topics": topics,
        "sources": sources,
        "language": language,
        "max_items": max_items,
        "summary_style": summary_style,
        "user_profile": {
            "explicit_preferences": explicit_preferences or [],
            "blocked_topics": blocked_topics or [],
            "time_decay_days": time_decay_days,
            "diversity_floor": diversity_floor,
        },
    }

    validated = validate_request(request)
    briefing = generate_briefing(validated, all_sources)

    if fmt == "markdown":
        return format_briefing_markdown(briefing)
    return json.dumps(briefing, ensure_ascii=False, indent=2)


@mcp.tool()
def list_sources_tool() -> str:
    """列出所有可用的信息源。

    返回信息源目录，包含每个源的 ID、名称、分类、接口类型、
    Agent 友好度等信息，帮助构造 briefing 请求。
    """
    sources = validate_sources(load_sources())
    summary = []
    for s in sources:
        summary.append(
            {
                "id": s["id"],
                "name": s["name"],
                "category": s["category"],
                "interface_types": s["interface_types"],
                "agent_friendly": s["agent_friendly"],
                "summary": s.get("summary", ""),
            }
        )
    return json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
def check_source_health_tool(source_ids: list[str] | None = None) -> str:
    """检查信息源的健康状态。

    对指定（或全部）信息源执行 ping 检查，返回每个源的可用状态。
    建议在生成简报前调用，确认数据源可达。

    Args:
        source_ids: 要检查的信息源 ID 列表。传 None 则检查全部。
    """
    from news_report.adapters import build_adapter_registry

    all_sources = validate_sources(load_sources())

    selected = [s for s in all_sources if s["id"] in source_ids] if source_ids else all_sources

    registry = build_adapter_registry(selected)
    results = []
    for s in selected:
        sid = s["id"]
        adapter = registry.get(sid)
        if adapter is None:
            results.append({"source_id": sid, "name": s["name"], "adapter": "none", "status": "no_adapter"})
            continue
        ok = adapter.ping()
        results.append(
            {
                "source_id": sid,
                "name": s["name"],
                "adapter": type(adapter).__name__,
                "status": "ok" if ok else "unreachable",
            }
        )
    return json.dumps(results, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("news-report://sources")
def sources_resource() -> str:
    """信息源目录 — data/sources.json 的完整内容。"""
    path = _DATA_DIR / "sources.json"
    return path.read_text(encoding="utf-8")


@mcp.resource("news-report://schema/briefing-request")
def briefing_request_schema_resource() -> str:
    """Briefing request 的 JSON Schema，用于构造合法请求。"""
    path = _SCHEMAS_DIR / "briefing-request.schema.json"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
