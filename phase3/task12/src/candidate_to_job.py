from __future__ import annotations

from typing import Mapping

from .features import candidate_job_features


def score_candidate_job(
    candidate: Mapping,
    job: Mapping,
) -> tuple[float, dict[str, float]]:
    features = candidate_job_features(candidate, job)

    score = (
        0.50 * features["skill_overlap"]
        + 0.25 * features["experience_match"]
        + 0.15 * features["location_match"]
        + 0.10 * features["popularity"]
    )

    return float(score), features


def recommend_jobs(
    candidate: Mapping,
    jobs: list[Mapping],
    top_k: int = 5,
) -> list[dict]:
    results = []

    for job in jobs:
        score, features = score_candidate_job(candidate, job)

        results.append(
            {
                "job_id": job["job_id"],
                "score": score,
                "features": features,
            }
        )

    results.sort(
        key=lambda row: (
            -row["score"],
            row["job_id"],
        )
    )

    for position, row in enumerate(results[:top_k], start=1):
        row["position"] = position

    return results[:top_k]