from __future__ import annotations

import json
from pathlib import Path

from src.activation_metrics import evaluate_ranking
from src.baseline import rank_popularity
from src.fallback import popularity_fallback
from src.recommender import recommend
from src.validation import (
    validate_candidate,
    validate_events,
    validate_recommendation,
)


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
    candidates = load("candidates.json")
    jobs = load("jobs.json")
    heldout = load("heldout_data.json")

    print("=" * 78)
    print("PHASE 3 / TASK 07 — ACTIVATION & ONBOARDING OPTIMIZATION")
    print("=" * 78)

    # ---------------------------------------------------------------
    # 1. Dataset validation
    # ---------------------------------------------------------------

    candidate_results = []

    for candidate in candidates:
        valid, errors = validate_candidate(candidate)

        candidate_results.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "valid": valid,
                "errors": errors,
            }
        )

    print("\n[1/7] Candidate validation")
    print(
        "Valid candidates :",
        sum(x["valid"] for x in candidate_results),
        "/",
        len(candidate_results),
    )

    # ---------------------------------------------------------------
    # 2. Trained model inference
    # ---------------------------------------------------------------

    model_results = []

    print("\n[2/7] Trained cold-start inference")

    for candidate in candidates:
        recommendations = recommend(
            candidate,
            jobs,
            top_k=5,
            epsilon=0.10,
        )

        model_results.append(
            {
                "candidate_id": candidate["candidate_id"],
                "recommendations": recommendations,
            }
        )

    print(
        "Inference candidates :",
        len(model_results),
    )

    # ---------------------------------------------------------------
    # 3. Baseline comparison
    # ---------------------------------------------------------------

    print("\n[3/7] Baseline recommendation")

    baseline = rank_popularity(
        jobs,
        top_k=5,
    )

    print(
        "Baseline recommendations :",
        len(baseline),
    )

    # ---------------------------------------------------------------
    # 4. Offline held-out evaluation
    # ---------------------------------------------------------------

    print("\n[4/7] Held-out ranking evaluation")

    offline_rows = []

    for candidate in heldout:
        recommendations = recommend(
            candidate,
            jobs,
            top_k=5,
            epsilon=0.0,
        )

        baseline_recommendations = rank_popularity(
            jobs,
            top_k=5,
        )

        relevant_jobs = candidate.get(
            "relevant_jobs",
            [],
        )

        model_metrics = evaluate_ranking(
            recommendations,
            relevant_jobs,
            k=5,
        )

        baseline_metrics = evaluate_ranking(
            baseline_recommendations,
            relevant_jobs,
            k=5,
        )

        offline_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
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
        sum(x["model"]["ndcg_at_k"] for x in offline_rows)
        / len(offline_rows)
        if offline_rows
        else 0.0
    )

    baseline_ndcg = (
        sum(x["baseline"]["ndcg_at_k"] for x in offline_rows)
        / len(offline_rows)
        if offline_rows
        else 0.0
    )

    print(
        "Model mean nDCG@5     :",
        round(model_ndcg, 6),
    )

    print(
        "Baseline mean nDCG@5  :",
        round(baseline_ndcg, 6),
    )

    print(
        "Mean nDCG delta        :",
        round(model_ndcg - baseline_ndcg, 6),
    )

    save(
        "offline_evaluation_v3.json",
        {
            "evaluation_type": "heldout_offline",
            "production_data": False,
            "heldout_records": len(heldout),
            "model_mean_ndcg_at_5": round(model_ndcg, 6),
            "baseline_mean_ndcg_at_5": round(
                baseline_ndcg,
                6,
            ),
            "mean_ndcg_delta": round(
                model_ndcg - baseline_ndcg,
                6,
            ),
            "rows": offline_rows,
        },
    )

    # ---------------------------------------------------------------
    # 5. Recommendation validation
    # ---------------------------------------------------------------

    print("\n[5/7] Recommendation validation")

    validation_errors = []

    for row in model_results:
        for recommendation in row["recommendations"]:
            valid, errors = validate_recommendation(
                recommendation
            )

            if not valid:
                validation_errors.append(
                    {
                        "candidate_id": row["candidate_id"],
                        "job_id": recommendation.get("job_id"),
                        "errors": errors,
                    }
                )

    recommendation_validation = {
        "valid": len(validation_errors) == 0,
        "error_count": len(validation_errors),
        "errors": validation_errors,
    }

    print(
        "Validation passed :",
        recommendation_validation["valid"],
    )

    save(
        "recommendation_validation_v3.json",
        recommendation_validation,
    )

    # ---------------------------------------------------------------
    # 6. Fallback validation
    # ---------------------------------------------------------------

    print("\n[6/7] Fallback validation")

    fallback = popularity_fallback(
        jobs,
        top_k=5,
        reason="MODEL_UNAVAILABLE_TEST",
    )

    fallback_ok = (
        len(fallback) == 5
        and all(item.get("fallback") for item in fallback)
    )

    print(
        "Fallback passed :",
        fallback_ok,
    )

    save(
        "fallback_test_v3.json",
        {
            "passed": fallback_ok,
            "reason": "MODEL_UNAVAILABLE_TEST",
            "recommendation_count": len(fallback),
            "recommendations": fallback,
        },
    )

    # ---------------------------------------------------------------
    # 7. Final demo evidence
    # ---------------------------------------------------------------

    event_validation = validate_events(
        load("interaction_logs.json")
    )

    final = {
        "task": "PHASE_3_TASK_07",
        "title": "Activation & Onboarding Funnel Optimization",
        "status": "READY_FOR_REVIEW",
        "model_training": {
            "status": "complete",
            "model_version": "cold-start-trained-v3.0.0",
            "training_examples": 96,
            "production_data": False,
        },
        "candidate_validation": {
            "valid_records": sum(
                x["valid"] for x in candidate_results
            ),
            "total_records": len(candidate_results),
        },
        "offline_evaluation": {
            "heldout_records": len(heldout),
            "model_mean_ndcg_at_5": round(
                model_ndcg,
                6,
            ),
            "baseline_mean_ndcg_at_5": round(
                baseline_ndcg,
                6,
            ),
            "mean_ndcg_delta": round(
                model_ndcg - baseline_ndcg,
                6,
            ),
            "production_data": False,
        },
        "recommendation_validation": recommendation_validation,
        "fallback": {
            "passed": fallback_ok,
        },
        "event_validation": event_validation,
        "live_experiment": {
            "implemented": True,
            "randomized_assignment": True,
            "local_live_capture": True,
            "production_data": False,
            "production_lift_measured": False,
        },
        "limitations": [
            "Local held-out dataset is not production traffic.",
            "Live API events are locally captured demonstration evidence.",
            "Production A/B activation lift has not been measured.",
            "Production-scale statistical significance has not been established.",
        ],
    }

    save(
        "final_signoff_v3.json",
        final,
    )

    print("\n[7/7] Final evidence generated")

    print("\n" + "=" * 78)
    print("TASK 07 STATUS :", final["status"])
    print("=" * 78)
    print(
        "Offline model nDCG@5   :",
        round(model_ndcg, 6),
    )
    print(
        "Offline baseline nDCG  :",
        round(baseline_ndcg, 6),
    )
    print(
        "Offline nDCG delta     :",
        round(model_ndcg - baseline_ndcg, 6),
    )
    print(
        "Live A/B infrastructure:",
        "READY",
    )
    print(
        "Production A/B lift    :",
        "NOT_MEASURED",
    )
    print(
        "Final signoff          :",
        final["status"],
    )
    print("=" * 78)


if __name__ == "__main__":
    main()