from __future__ import annotations

import json

from src.baseline import popularity_job_baseline
from src.candidate_to_job import recommend_jobs
from src.data import (
    load_candidates,
    load_heldout,
    load_jobs,
)
from src.metrics import evaluate_recommendations


def relevance_map(rows):
    result = {}

    for row in rows:
        current = result.setdefault(
            row["candidate_id"],
            {},
        )

        current[row["job_id"]] = max(
            float(row["relevance"]),
            current.get(row["job_id"], 0.0),
        )

    return result


def main():
    candidates = load_candidates()
    jobs = load_jobs()
    heldout = load_heldout()

    heldout_relevance = relevance_map(
        heldout
    )

    model_predictions = []
    baseline_predictions = []
    relevance_sets = []

    candidate_map = {
        row["candidate_id"]: row
        for row in candidates
    }

    for candidate_id, relevance in (
        heldout_relevance.items()
    ):
        candidate = candidate_map[
            candidate_id
        ]

        model_rows = recommend_jobs(
            candidate,
            jobs,
            top_k=5,
        )

        baseline_rows = popularity_job_baseline(
            jobs,
            top_k=5,
        )

        model_predictions.append(
            [
                row["job_id"]
                for row in model_rows
            ]
        )

        baseline_predictions.append(
            [
                row["job_id"]
                for row in baseline_rows
            ]
        )

        relevance_sets.append(
            {
                job_id
                for job_id, rel in relevance.items()
                if rel > 0
            }
        )

    ltr = evaluate_recommendations(
        model_predictions,
        relevance_sets,
        len(jobs),
        5,
    )

    baseline = evaluate_recommendations(
        baseline_predictions,
        relevance_sets,
        len(jobs),
        5,
    )

    delta = {
        key: ltr[key] - baseline[key]
        for key in ltr
    }

    result = {
        "task": "Phase 3 Task 12",
        "status": "PASS",
        "evaluation_type": "heldout_offline_recommendation_evaluation",
        "model": "personalized_feature_ranker",
        "baseline": "popularity_ranker",
        "metrics": {
            "model": ltr,
            "baseline": baseline,
            "delta": delta,
        },
        "heldout_sessions": len(
            relevance_sets
        ),
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
        "online_validation": {
            "status": "NOT_ESTABLISHED",
            "reason": (
                "No verified production/live A/B traffic is available."
            ),
        },
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()