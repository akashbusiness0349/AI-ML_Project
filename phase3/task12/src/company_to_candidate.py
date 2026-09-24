from __future__ import annotations

from typing import Mapping

from .features import company_candidate_features


def score_company_candidate(
    company: Mapping,
    candidate: Mapping,
) -> tuple[float, dict[str, float]]:
    features = company_candidate_features(
        company,
        candidate,
    )

    score = (
        0.55 * features["skill_overlap"]
        + 0.25 * features["experience_match"]
        + 0.20 * features["location_match"]
    )

    return float(score), features


def recommend_candidates(
    company: Mapping,
    candidates: list[Mapping],
    top_k: int = 5,
) -> list[dict]:
    results = []

    for candidate in candidates:
        score, features = score_company_candidate(
            company,
            candidate,
        )

        results.append(
            {
                "candidate_id": candidate["candidate_id"],
                "score": score,
                "features": features,
            }
        )

    results.sort(
        key=lambda row: (
            -row["score"],
            row["candidate_id"],
        )
    )

    for position, row in enumerate(results[:top_k], start=1):
        row["position"] = position

    return results[:top_k]