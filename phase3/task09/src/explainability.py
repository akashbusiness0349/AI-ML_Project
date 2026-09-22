from __future__ import annotations

from typing import Any

import pandas as pd


def explain_prediction(
    entity_id: str,
    variant: str,
    score: float,
    features: pd.Series | dict[str, Any],
) -> dict[str, Any]:
    if isinstance(features, pd.Series):
        values = features.to_dict()
    else:
        values = dict(features)

    reasons: list[str] = []

    if float(values.get("engagement_score", 0)) >= 0.70:
        reasons.append("recent engagement is high")
    elif float(values.get("engagement_score", 0)) < 0.35:
        reasons.append("engagement is low")

    if float(values.get("events_7d", 0)) >= 8:
        reasons.append("activity during the last 7 days is high")
    elif float(values.get("events_7d", 0)) <= 2:
        reasons.append("activity during the last 7 days is low")

    if float(values.get("days_since_last_event", 30)) >= 7:
        reasons.append("the last activity is relatively old")
    else:
        reasons.append("the entity was active recently")

    if float(values.get("hiring_relevance", 0)) >= 0.70:
        reasons.append("hiring relevance is high")

    if not reasons:
        reasons.append("no single feature dominates the score")

    return {
        "entity_id": str(entity_id),
        "variant": variant,
        "score": round(float(score), 6),
        "plain_english_reason": (
            f"The {variant} score is {score:.3f} because "
            + "; ".join(reasons)
            + "."
        ),
    }