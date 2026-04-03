from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import jsonschema

from news_report.adapters import build_adapter_registry
from news_report.cache import cache_key, cache_read, cache_write

logger = logging.getLogger(__name__)

ALLOWED_SUMMARY_STYLES = {"headline_only", "concise", "detailed"}


def _resolve_dir(name: str) -> Path:
    """Resolve data/schemas dir: repo root first, then inside the installed package."""
    pkg = Path(__file__).resolve().parent
    repo = pkg.parent / name
    if repo.is_dir():
        return repo
    return pkg / name


_SCHEMAS_DIR = _resolve_dir("schemas")


def _load_schema(name: str) -> dict:
    path = _SCHEMAS_DIR / name
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


AGENT_FRIENDLY_WEIGHT = {"low": 0.2, "medium": 0.6, "high": 1.0}
INTERFACE_WEIGHT = {"web": 0.2, "rss": 0.5, "api": 0.8, "cli": 0.85, "mcp": 1.0, "email": 0.3}


def validate_request(request: object) -> dict:
    """Validate a briefing request against the JSON Schema."""
    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object")
    try:
        schema = _load_schema("briefing-request.schema.json")
        jsonschema.validate(instance=request, schema=schema)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"Invalid request: {exc.message}") from exc
    return request


def normalize_terms(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value.strip()]


def compute_score(
    candidate: dict,
    request: dict,
    selected_sources: list[dict],
    source_counts: dict[str, int],
) -> tuple[float, dict]:
    profile = request["user_profile"]
    topics = normalize_terms(request["topics"])
    preferences = normalize_terms(profile["explicit_preferences"])
    blocked = normalize_terms(profile["blocked_topics"])
    candidate_terms = normalize_terms(candidate["tags"] + candidate["angles"] + [candidate["content_type"]])

    if any(blocked_term and blocked_term in " ".join(candidate_terms) for blocked_term in blocked):
        return -1.0, {}

    topic_match = 1.0 if any(topic in candidate["title"].lower() for topic in topics) else 0.4
    preference_overlap = len(set(preferences) & set(candidate_terms))
    preference_match = min(1.0, preference_overlap / max(1, len(preferences)))

    age_days = max(0, (datetime.now(UTC) - candidate["published_at"]).days)
    freshness = max(0.1, 1 - (age_days / max(1, profile["time_decay_days"])))

    source = candidate["source_meta"]
    source_quality = 0.6 * AGENT_FRIENDLY_WEIGHT.get(source["agent_friendly"], 0.2)
    interface_score = max(INTERFACE_WEIGHT.get(value, 0.1) for value in source["interface_types"])
    source_quality += 0.4 * interface_score

    diversity_floor = float(profile["diversity_floor"])
    source_share = source_counts[candidate["source"]] / max(1, len(selected_sources))
    diversity = max(diversity_floor, 1 - max(0, source_share - diversity_floor))

    score_breakdown = {
        "source_quality": round(source_quality, 3),
        "topic_match": round(topic_match, 3),
        "preference_match": round(preference_match, 3),
        "freshness": round(freshness, 3),
        "diversity": round(diversity, 3),
    }

    score = 0.3 * source_quality + 0.25 * topic_match + 0.2 * preference_match + 0.15 * freshness + 0.1 * diversity
    return round(score, 4), score_breakdown


def rerank_with_diversity(scored_items: list[dict], max_items: int, diversity_floor: float) -> list[dict]:
    if not scored_items:
        return []

    remaining = sorted(scored_items, key=lambda item: item["score"], reverse=True)
    selected = []
    selected_by_source: dict[str, int] = {}

    while remaining and len(selected) < max_items:
        best_index = 0
        best_score = -1.0

        for index, item in enumerate(remaining):
            prior_count = selected_by_source.get(item["source"], 0)
            penalty = prior_count * max(0.12, 1 - diversity_floor)
            adjusted_score = item["score"] - penalty
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_index = index

        chosen = remaining.pop(best_index)
        selected.append(chosen)
        selected_by_source[chosen["source"]] = selected_by_source.get(chosen["source"], 0) + 1

    return selected


def format_why(candidate: dict, request: dict, breakdown: dict) -> str:
    preferences = normalize_terms(request["user_profile"]["explicit_preferences"])
    matched_preferences = [tag for tag in candidate["tags"] if tag.lower() in preferences]
    reasons = [
        f"strong topic match for {', '.join(request['topics'])}",
        f"source quality={breakdown['source_quality']}",
        f"freshness={breakdown['freshness']}",
    ]
    if matched_preferences:
        reasons.append(f"matched explicit preferences: {', '.join(matched_preferences)}")
    return "; ".join(reasons)


def generate_briefing(request: dict, sources: list[dict], *, use_cache: bool = True) -> dict:
    # --- cache check ---
    key = cache_key(request)
    if use_cache:
        cached = cache_read(key)
        if cached is not None:
            return cached

    source_index = {source["id"]: source for source in sources}
    selected_sources = [source_index[source_id] for source_id in request["sources"] if source_id in source_index]
    if not selected_sources:
        raise ValueError("No requested sources matched data/sources.json")

    registry = build_adapter_registry(selected_sources)
    now = datetime.now(UTC)
    candidates = []
    source_counts: dict[str, int] = {}

    for topic in request["topics"]:
        for source in selected_sources:
            fetched = registry[source["id"]].fetch(topic, request["summary_style"], now=now)
            source_counts[source["id"]] = source_counts.get(source["id"], 0) + len(fetched)
            candidates.extend(fetched)

    scored_items = []
    for candidate in candidates:
        score, breakdown = compute_score(candidate, request, selected_sources, source_counts)
        if score < 0:
            continue
        scored_items.append(
            {
                "id": candidate["id"],
                "title": candidate["title"],
                "source": candidate["source"],
                "content_type": candidate["content_type"],
                "url": candidate["url"],
                "published_at": candidate["published_at"].isoformat().replace("+00:00", "Z"),
                "summary": candidate["summary"],
                "why_it_matters": format_why(candidate, request, breakdown),
                "score": score,
                "score_breakdown": breakdown,
                "tags": candidate["tags"],
            }
        )

    items = rerank_with_diversity(
        scored_items,
        request["max_items"],
        float(request["user_profile"]["diversity_floor"]),
    )

    briefing = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "query": {
            "topics": request["topics"],
            "sources": request["sources"],
            "language": request["language"],
            "max_items": request["max_items"],
            "summary_style": request["summary_style"],
        },
        "items": items,
        "coverage": {
            "requested_sources": len(request["sources"]),
            "matched_sources": len(selected_sources),
            "generated_candidates": len(candidates),
            "returned_items": len(items),
        },
    }

    # --- cache write ---
    if use_cache:
        cache_write(key, briefing)

    return briefing
