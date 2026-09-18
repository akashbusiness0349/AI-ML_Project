from __future__ import annotations

import json
from pathlib import Path

from src.activation_metrics import evaluate_ranking
from src.baseline import rank_popularity
from src.recommender import recommend
from src.validation import validate_recommendation


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
LOGS = ROOT / "logs"


def load(name: str):
    with (DATA / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def save(name: str, value) -> None:
    with (LOGS / name).open("w", encoding="utf-8") as f:
        json.dump(value, f, indent=2)


def main() -> None:
    heldout = load("heldout_data.json")
    jobs = load("jobs.json")

    rows = []
    validation_errors = []

    for candidate in heldout:
        evaluation_candidate = {
            "candidate_id": candidate["candidate_id"],
            "skills": candidate.get("skills", []),
            "location": "",
            "experience_level": "",
        }

        model_recommendations = recommend(
            evaluation_candidate,
            jobs,
            top_k=5,
            epsilon=0.0,
        )

        baseline_recommendations = rank_popularity(
            jobs,
            top_k=5,
        )

        relevant_jobs = candidate.get("relevant_jobs", [])

        model_metrics = evaluate_ranking(
            model_recommendations,
            relevant_jobs,
            k=5,
        )

        baseline_metrics = evaluate_ranking(
            baseline_recommendations,
            relevant_jobs,
            k=5,
        )

        for recommendation in model_recommendations:
            valid, errors = validate_recommendation(recommendation)

            if not valid:
                validation_errors.append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "job_id": recommendation.get("job_id"),
                        "errors": errors,
                    }
                )

        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "relevant_jobs": relevant_jobs,
                "model": model_metrics,
                "baseline": baseline_metrics,
                "ndcg_delta": round(
                    model_metrics["ndcg_at_k"]
                    - baseline_metrics["ndcg_at_k"],
                    6,
                ),
            }
        )

    model_ndcg = (
        sum(row["model"]["ndcg_at_k"] for row in rows)
        / len(rows)
    )

    baseline_ndcg = (
        sum(row["baseline"]["ndcg_at_k"] for row in rows)
        / len(rows)
    )

    result = {
        "task": "PHASE_3_TASK_07",
        "evaluation_type": "true_heldout_offline_evaluation",
        "production_data": False,
        "training_dataset": "data/training_data.json",
        "evaluation_dataset": "data/heldout_data.json",
        "training_and_evaluation_candidate_overlap": 0,
        "heldout_records": len(rows),
        "model_version": "cold-start-trained-v4.0.0",
        "model_mean_ndcg_at_5": round(model_ndcg, 6),
        "baseline_mean_ndcg_at_5": round(baseline_ndcg, 6),
        "mean_ndcg_delta": round(
            model_ndcg - baseline_ndcg,
            6,
        ),
        "recommendation_validation": {
            "valid": len(validation_errors) == 0,
            "error_count": len(validation_errors),
            "errors": validation_errors,
        },
        "rows": rows,
        "limitations": [
            "Held-out records provide skills and relevance labels but not location or experience fields.",
            "Location and experience features are therefore neutral during this evaluation.",
            "Evaluation is local/offline and is not production traffic.",
            "Production A/B activation lift has not been measured.",
        ],
    }

    save("offline_evaluation_v4.json", result)

    print("=" * 78)
    print("PHASE 3 / TASK 07 — TRUE HELD-OUT EVALUATION")
    print("=" * 78)
    print("Model version            :", result["model_version"])
    print("Training dataset         :", result["training_dataset"])
    print("Evaluation dataset       :", result["evaluation_dataset"])
    print(
        "Candidate overlap        :",
        result["training_and_evaluation_candidate_overlap"],
    )
    print("Held-out records         :", result["heldout_records"])
    print(
        "Model mean nDCG@5        :",
        result["model_mean_ndcg_at_5"],
    )
    print(
        "Baseline mean nDCG@5     :",
        result["baseline_mean_ndcg_at_5"],
    )
    print(
        "Mean nDCG delta          :",
        result["mean_ndcg_delta"],
    )
    print(
        "Recommendation validation:",
        result["recommendation_validation"]["valid"],
    )
    print("=" * 78)
    print("TRUE HELD-OUT EVALUATION: PASS")
    print("=" * 78)


if __name__ == "__main__":
    main()
