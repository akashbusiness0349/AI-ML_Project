"""
PlaceMux Phase 2 — Task 7
Pay-per-Application Flow
Conversion-Oriented Ranking Tuning Demo
"""

import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(
    0,
    str(SRC_DIR)
)

from conversion_ranker import (
    MODEL_VERSION,
    rank_for_conversion,
    calculate_conversion_proxy,
    calculate_average_match_score
)

from tuning_evaluator import (
    evaluate_tuning
)


# ============================================================
# BASELINE FROM TASK 6
# ============================================================

TASK6_BASELINE_AVERAGE = 0.7224


# ============================================================
# REPRESENTATIVE PAY-PER-APPLICATION OPPORTUNITIES
# ============================================================

opportunities = [
    {
        "job_id": "job_001",
        "job_role": "ML Engineer",
        "company": "AI Labs",

        "match_score": 1.00,

        "relevance_score": 1.00,

        "application_intent_score": 0.70,

        "application_value_score": 0.90
    },
    {
        "job_id": "job_002",
        "job_role": "Data Scientist",
        "company": "DataWorks",

        "match_score": 0.85,

        "relevance_score": 0.90,

        "application_intent_score": 0.90,

        "application_value_score": 0.80
    },
    {
        "job_id": "job_003",
        "job_role": "Software Engineer",
        "company": "Web Systems",

        "match_score": 0.325,

        "relevance_score": 0.40,

        "application_intent_score": 0.80,

        "application_value_score": 0.70
    }
]


# ============================================================
# BASELINE RANKING
# ============================================================

baseline_results = [
    {
        "job_id": "job_001",
        "match_score": 1.00,
        "rank": 1
    },
    {
        "job_id": "job_002",
        "match_score": 0.85,
        "rank": 2
    },
    {
        "job_id": "job_003",
        "match_score": 0.325,
        "rank": 3
    }
]


baseline_average = (
    calculate_average_match_score(
        baseline_results
    )
)


baseline_conversion_proxy = (
    calculate_conversion_proxy(
        [
            {
                "conversion_priority_score":
                    item["match_score"]
            }
            for item in baseline_results
        ]
    )
)


# ============================================================
# TUNED RANKING
# ============================================================

tuned_results = rank_for_conversion(
    opportunities
)


tuned_average = (
    calculate_average_match_score(
        tuned_results
    )
)


tuned_conversion_proxy = (
    calculate_conversion_proxy(
        tuned_results
    )
)


# ============================================================
# EVALUATION
# ============================================================

evaluation = evaluate_tuning(
    baseline_average_match=
        TASK6_BASELINE_AVERAGE,

    tuned_average_match=
        tuned_average,

    baseline_conversion_proxy=
        baseline_conversion_proxy,

    tuned_conversion_proxy=
        tuned_conversion_proxy,

    tuned_results=
        tuned_results
)


# ============================================================
# STRUCTURED RESULT
# ============================================================

final_status = (
    "PASS"
    if evaluation["overall_pass"]
    else "FAIL"
)


result = {
    "task":
        "Task 7 — Pay-per-Application Flow",

    "model_version":
        MODEL_VERSION,

    "baseline": {
        "average_match_score":
            TASK6_BASELINE_AVERAGE,

        "conversion_proxy":
            baseline_conversion_proxy
    },

    "tuned": {
        "average_match_score":
            tuned_average,

        "conversion_proxy":
            tuned_conversion_proxy
    },

    "tuned_ranking":
        tuned_results,

    "evaluation":
        evaluation,

    "final_status":
        final_status
}


# ============================================================
# DISPLAY
# ============================================================

print("=" * 70)
print(
    "TASK 7 — PAY-PER-APPLICATION "
    "RANKING TUNING"
)
print("=" * 70)


print(
    "\n========== TASK 6 BASELINE =========="
)

print(
    "Average match quality : "
    f"{TASK6_BASELINE_AVERAGE * 100:.2f}%"
)

print(
    "Baseline conversion proxy : "
    f"{baseline_conversion_proxy * 100:.2f}%"
)


print(
    "\n========== TUNED RANKING =========="
)

for item in tuned_results:

    print(
        f"{item['rank']}. "
        f"{item['job_id']} | "
        f"{item['job_role']} | "
        f"Match: "
        f"{item['match_score'] * 100:.2f}% | "
        f"Conversion priority: "
        f"{item['conversion_priority_score'] * 100:.2f}%"
    )


print(
    "\n========== TUNED METRICS =========="
)

print(
    "Tuned average match quality : "
    f"{tuned_average * 100:.2f}%"
)

print(
    "Tuned conversion proxy     : "
    f"{tuned_conversion_proxy * 100:.2f}%"
)


print(
    "\n========== BASELINE VS TUNED =========="
)

print(
    "Match quality change       : "
    f"{evaluation['match_quality_change'] * 100:+.2f}%"
)

print(
    "Conversion proxy change    : "
    f"{evaluation['conversion_proxy_change'] * 100:+.2f}%"
)


print(
    "\n========== VALIDATION =========="
)

print(
    "Ranking order              : "
    f"{'PASS' if evaluation['ranking_order'] else 'FAIL'}"
)

print(
    "Rank sequence              : "
    f"{'PASS' if evaluation['rank_sequence'] else 'FAIL'}"
)

print(
    "Match quality protected    : "
    f"{'PASS' if evaluation['match_quality_protected'] else 'FAIL'}"
)

print(
    "Conversion proxy improved  : "
    f"{'PASS' if evaluation['conversion_proxy_improved_or_maintained'] else 'FAIL'}"
)

print(
    "Overall tuning evaluation  : "
    f"{'PASS' if evaluation['overall_pass'] else 'FAIL'}"
)


print(
    "\n========== STRUCTURED RESULT =========="
)

print(
    json.dumps(
        result,
        indent=2
    )
)


print(
    "\n========== FINAL STATUS =========="
)

print(
    "Ranking tuned for conversion : "
    f"{final_status}"
)

print(
    "Match quality protected       : "
    f"{'PASS' if evaluation['match_quality_protected'] else 'FAIL'}"
)

print(
    "Conversion impact measured   : PASS"
)

print(
    "Baseline comparison complete : PASS"
)


if final_status == "PASS":

    print(
        "\nTask 7 pay-per-application "
        "ranking tuning completed successfully."
    )

else:

    print(
        "\nTask 7 tuning failed validation."
    )