from __future__ import annotations

from typing import Mapping

from .features import build_feature_dict


def heuristic_score(
    candidate: Mapping,
    job: Mapping,
) -> float:
    features = build_feature_dict(
        candidate,
        job,
    )

    return (
        0.45 * features["skill_overlap"]
        + 0.25 * features["experience_match"]
        + 0.20 * features["location_match"]
        + 0.10 * features["job_popularity"]
    )


def rank_jobs_baseline(
    candidate: Mapping,
    jobs: list[Mapping],
) -> list[dict]:
    ranked = []

    for job in jobs:
        score = heuristic_score(
            candidate,
            job,
        )

        ranked.append(
            {
                "job_id": job["job_id"],
                "score": float(score),
            }
        )

    ranked.sort(
        key=lambda x: (-x["score"], x["job_id"])
    )

    for position, row in enumerate(
        ranked,
        start=1,
    ):
        row["position"] = position

    return ranked