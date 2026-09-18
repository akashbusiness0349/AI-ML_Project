"""
Task 07 — Baseline Recommendation Strategy

Popularity-only baseline used for comparison with the trained model.
"""

from __future__ import annotations

from typing import Any


def popularity_score(job: dict[str, Any]) -> float:
    return float(job.get("popularity", 0) or 0)


def rank_popularity(
    jobs: list[dict[str, Any]],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    ranked = []

    for job in jobs:
        ranked.append(
            {
                "job_id": job.get("job_id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "score": round(popularity_score(job) / 100.0, 8),
                "strategy": "popularity_baseline",
            }
        )

    ranked.sort(
        key=lambda item: (
            item["score"],
            item["job_id"],
        ),
        reverse=True,
    )

    return ranked[:top_k]


# Compatibility alias for older code.
popularity_rank = rank_popularity