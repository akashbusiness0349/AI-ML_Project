from __future__ import annotations

from typing import Any


def non_ml_baseline_score(features: dict[str, Any]) -> float:
    """
    Deterministic non-ML baseline.

    Higher engagement, recent activity and hiring relevance
    produce a higher score.

    This is intentionally transparent and model-free.
    """
    engagement = float(features.get("engagement_score", 0.0))
    events_1d = float(features.get("events_1d", 0.0))
    events_7d = float(features.get("events_7d", 0.0))
    hiring = float(features.get("hiring_relevance", 0.0))
    days_since_last = float(
        features.get("days_since_last_event", 30.0)
    )

    recency_component = max(
        0.0,
        1.0 - min(days_since_last / 14.0, 1.0),
    )

    activity_component = min(
        (events_1d * 0.25 + events_7d * 0.05),
        1.0,
    )

    score = (
        0.30 * engagement
        + 0.25 * recency_component
        + 0.20 * activity_component
        + 0.25 * hiring
    )

    return float(max(0.0, min(1.0, score)))


def fallback_response(
    entity_id: str,
    reason: str,
    features: dict[str, Any],
) -> dict[str, Any]:
    return {
        "entity_id": str(entity_id),
        "decision": "NON_ML_FALLBACK",
        "score": non_ml_baseline_score(features),
        "reason": reason,
        "safe": True,
    }