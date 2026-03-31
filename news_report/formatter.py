"""Briefing output formatters."""

from __future__ import annotations


def format_briefing_markdown(briefing: dict) -> str:
    """Render a briefing dict as human-readable Markdown."""
    lines: list[str] = []
    generated_at = briefing.get("generated_at", "unknown")
    lines.append(f"# News Briefing — {generated_at[:10]}")
    lines.append("")

    items = briefing.get("items", [])
    if not items:
        lines.append("_No items matched your query._")
        lines.append("")
        return "\n".join(lines)

    for idx, item in enumerate(items, 1):
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        source = item.get("source", "unknown")
        content_type = item.get("content_type", "article")
        score = item.get("score", 0)
        why = item.get("why_it_matters", "")
        summary = item.get("summary", "")

        if url:
            lines.append(f"## {idx}. [{title}]({url})")
        else:
            lines.append(f"## {idx}. {title}")

        lines.append(f"- **Source:** {source} | **Type:** {content_type}")
        lines.append(f"- **Score:** {score:.2f}")
        if why:
            lines.append(f"- **Why:** {why}")
        if summary:
            lines.append(f"- {summary}")
        lines.append("")

    # Coverage footer
    cov = briefing.get("coverage", {})
    lines.append("---")
    lines.append(
        f"Sources: {cov.get('matched_sources', '?')}/{cov.get('requested_sources', '?')} matched · "
        f"Candidates: {cov.get('generated_candidates', '?')} · "
        f"Returned: {cov.get('returned_items', '?')}"
    )
    lines.append("")
    return "\n".join(lines)
