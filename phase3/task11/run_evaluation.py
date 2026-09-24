from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict

from src.baseline import heuristic_score
from src.data import (
    load_candidates,
    load_heldout,
    load_jobs,
    save_json,
)
from src.metrics import (
    average_precision,
    ndcg,
    precision_at_k,
)
from src.ranker import load_model


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "task11_ltr_model.joblib"
)


def aggregate_relevance(
    heldout: list[dict],
) -> dict[str, dict[str, int]]:
    result = defaultdict(dict)

    for row in heldout:
        candidate_id = row["candidate_id"]
        job_id = row["job_id"]

        result[candidate_id][job_id] = int(
            row.get("relevance", 0)
        )

    return dict(result)


def rank_with_scores(
    candidate: dict,
    jobs: list[dict],
    model,
    relevance_map: dict[str, int],
):
    ltr = []
    baseline = []

    for job in jobs:
        job_id = job["job_id"]
        relevance = relevance_map.get(
            job_id,
            0,
        )

        ltr.append(
            {
                "job_id": job_id,
                "score": model.score(
                    candidate,
                    job,
                ),
                "relevance": relevance,
            }
        )

        baseline.append(
            {
                "job_id": job_id,
                "score": heuristic_score(
                    candidate,
                    job,
                ),
                "relevance": relevance,
            }
        )

    ltr.sort(
        key=lambda x: (
            -x["score"],
            x["job_id"],
        )
    )

    baseline.sort(
        key=lambda x: (
            -x["score"],
            x["job_id"],
        )
    )

    return ltr, baseline


def main() -> None:
    candidates = load_candidates()
    jobs = load_jobs()
    heldout = load_heldout()

    model = load_model(
        MODEL_PATH
    )

    candidate_map = {
        row["candidate_id"]: row
        for row in candidates
    }

    relevance_by_candidate = (
        aggregate_relevance(
            heldout
        )
    )

    ltr_rankings = []
    baseline_rankings = []

    per_candidate = []

    for candidate_id, relevance_map in (
        relevance_by_candidate.items()
    ):
        if candidate_id not in candidate_map:
            continue

        candidate = candidate_map[
            candidate_id
        ]

        ltr, baseline = rank_with_scores(
            candidate,
            jobs,
            model,
            relevance_map,
        )

        ltr_rel = [
            row["relevance"]
            for row in ltr
        ]

        baseline_rel = [
            row["relevance"]
            for row in baseline
        ]

        ideal = sorted(
            relevance_map.values(),
            reverse=True,
        )

        ltr_rankings.append(
            ltr_rel
        )

        baseline_rankings.append(
            baseline_rel
        )

        per_candidate.append(
            {
                "candidate_id": candidate_id,
                "ltr": {
                    "nDCG@5": ndcg(
                        ltr_rel,
                        ideal,
                        5,
                    ),
                    "nDCG@10": ndcg(
                        ltr_rel,
                        ideal,
                        10,
                    ),
                    "MAP": average_precision(
                        ltr_rel
                    ),
                    "Precision@5": precision_at_k(
                        ltr_rel,
                        5,
                    ),
                },
                "baseline": {
                    "nDCG@5": ndcg(
                        baseline_rel,
                        ideal,
                        5,
                    ),
                    "nDCG@10": ndcg(
                        baseline_rel,
                        ideal,
                        10,
                    ),
                    "MAP": average_precision(
                        baseline_rel
                    ),
                    "Precision@5": precision_at_k(
                        baseline_rel,
                        5,
                    ),
                },
                "ltr_top5": ltr[:5],
                "baseline_top5": baseline[:5],
            }
        )

    metrics = [
        "nDCG@5",
        "nDCG@10",
        "MAP",
        "Precision@5",
    ]

    summary = {
        "ltr": {},
        "baseline": {},
        "delta": {},
    }

    for metric in metrics:
        ltr_value = (
            sum(
                row["ltr"][metric]
                for row in per_candidate
            )
            / len(per_candidate)
        )

        baseline_value = (
            sum(
                row["baseline"][metric]
                for row in per_candidate
            )
            / len(per_candidate)
        )

        summary["ltr"][metric] = (
            ltr_value
        )

        summary["baseline"][metric] = (
            baseline_value
        )

        summary["delta"][metric] = (
            ltr_value
            - baseline_value
        )

    output = {
        "task": "Phase 3 Task 11",
        "status": "PASS",
        "evaluation_type": (
            "heldout_offline_ranking_evaluation"
        ),
        "candidate_count": len(
            per_candidate
        ),
        "heldout_impression_count": len(
            heldout
        ),
        "baseline": "heuristic_ranker",
        "model": "pairwise_ltr",
        "metrics": summary,
        "per_candidate": per_candidate,
        "online_validation": {
            "status": "NOT_ESTABLISHED",
            "reason": (
                "No verified production/live "
                "A/B traffic is available."
            ),
        },
    }

    save_json(
        output,
        "logs/evaluation_result.json",
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()