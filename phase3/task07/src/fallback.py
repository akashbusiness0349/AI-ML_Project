"""
Task 07 — Recommendation Fallback

Safe recommendation path when the trained model is unavailable.
"""

from __future__ import annotations

from typing import Any

from .baseline import rank_popularity


def popularity_fallback(
    jobs: list[dict[str, Any]],
    top_k: int = 5,
    reason: str = "MODEL_UNAVAILABLE",
) -> list[dict[str, Any]]:
    recommendations = rank_popularity(
        jobs,
        top_k=top_k,
    )

    for item in recommendations:
        item["fallback"] = True
        item["fallback_reason"] = reason

    return recommendations


# Compatibility alias.
safe_fallback = popularity_fallback