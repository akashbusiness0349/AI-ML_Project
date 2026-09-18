"""
Task 07 — Recommendation Service

Thin inference layer around the trained cold-start model.
"""

from __future__ import annotations

from typing import Any

from .cold_start import (
    explain_recommendation,
    load_model,
    rank_candidate,
)


def recommend(
    candidate: dict[str, Any],
    jobs: list[dict[str, Any]],
    top_k: int = 5,
    epsilon: float = 0.10,
) -> list[dict[str, Any]]:
    model = load_model()

    recommendations = rank_candidate(
        candidate=candidate,
        jobs=jobs,
        model=model,
        top_k=top_k,
        epsilon=epsilon,
    )

    for item in recommendations:
        item["explanation"] = explain_recommendation(item)

    return recommendations