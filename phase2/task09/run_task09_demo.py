"""
PlaceMux Phase 2 — Task 9
Failure Handling & Resilience
Conversion-Quality Check Demo
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

from conversion_quality_evaluator import (
    evaluate_conversion_quality
)


# ============================================================
# BASELINE — BEFORE PAYWALL
# ============================================================

baseline_results = [
    {
        "job_id": "job_001",
        "job_role": "ML Engineer",
        "match_score": 1.00,
        "relevant": True
    },
    {
        "job_id": "job_002",
        "job_role": "Data Scientist",
        "match_score": 0.85,
        "relevant": True
    },
    {
        "job_id": "job_003",
        "job_role": "Software Engineer",
        "match_score": 0.325,
        "relevant": False
    }
]


# ============================================================
# POST-PAYWALL
# ============================================================

post_paywall_results = [
    {
        "job_id": "job_001",
        "job_role": "ML Engineer",
        "match_score": 1.00,
        "relevant": True
    },
    {
        "job_id": "job_002",
        "job_role": "Data Scientist",
        "match_score": 0.85,
        "relevant": True
    },
    {
        "job_id": "job_003",
        "job_role": "Software Engineer",
        "match_score": 0.325,
        "relevant": False
    }
]


# ============================================================
# EVALUATION
# ============================================================

evaluation = evaluate_conversion_quality(
    baseline_results=baseline_results,
    post_paywall_results=post_paywall_results
)


result = {
    "task":
        "Task 9 — Failure Handling & Resilience",

    **evaluation
}


# ============================================================
# DISPLAY
# ============================================================

print("=" * 70)
print(
    "TASK 9 — CONVERSION-QUALITY CHECK"
)
print("=" * 70)


print(
    "\n========== BASELINE — BEFORE PAYWALL =========="
)

baseline = evaluation[
    "baseline_metrics"
]

print(
    "Average match score : "
    f"{baseline['average_match_score'] * 100:.2f}%"
)

print(
    "Top-1 relevance     : "
    f"{baseline['top_1_relevance'] * 100:.2f}%"
)

print(
    "Top-3 relevance     : "
    f"{baseline['top_3_relevance'] * 100:.2f}%"
)

print(
    "Ranking consistency : "
    f"{'PASS' if baseline['ranking_consistency'] else 'FAIL'}"
)


print(
    "\n========== POST-PAYWALL =========="
)

post = evaluation[
    "post_paywall_metrics"
]

print(
    "Average match score : "
    f"{post['average_match_score'] * 100:.2f}%"
)

print(
    "Top-1 relevance     : "
    f"{post['top_1_relevance'] * 100:.2f}%"
)

print(
    "Top-3 relevance     : "
    f"{post['top_3_relevance'] * 100:.2f}%"
)

print(
    "Ranking consistency : "
    f"{'PASS' if post['ranking_consistency'] else 'FAIL'}"
)


print(
    "\n========== CONVERSION QUALITY =========="
)

print(
    "Baseline quality : "
    f"{evaluation['baseline_conversion_quality'] * 100:.2f}%"
)

print(
    "Post-paywall quality : "
    f"{evaluation['post_paywall_conversion_quality'] * 100:.2f}%"
)

print(
    "Quality change : "
    f"{evaluation['conversion_quality_change'] * 100:+.2f}%"
)


print(
    "\n========== REGRESSION CHECK =========="
)

regression = evaluation[
    "regression_check"
]

print(
    "Average score change : "
    f"{regression['changes']['average_score_change'] * 100:+.2f}%"
)

print(
    "Top-1 relevance change : "
    f"{regression['changes']['top_1_relevance_change'] * 100:+.2f}%"
)

print(
    "Top-3 relevance change : "
    f"{regression['changes']['top_3_relevance_change'] * 100:+.2f}%"
)

print(
    "Allowed relevance drop : "
    f"{regression['allowed_relevance_drop'] * 100:.2f}%"
)

print(
    "Regression detected : "
    f"{regression['regression_detected']}"
)


print(
    "\n========== VALIDATION =========="
)

print(
    "No relevance regression detected : "
    f"{'PASS' if evaluation['no_relevance_regression'] else 'FAIL'}"
)

print(
    "Ranking consistency : "
    f"{'PASS' if evaluation['ranking_consistency'] else 'FAIL'}"
)

print(
    "Overall conversion-quality check : "
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

if evaluation["overall_pass"]:

    print(
        "No relevance regression detected : PASS"
    )

    print(
        "Paywall relevance protection : PASS"
    )

    print(
        "Conversion-quality check : PASS"
    )

    print(
        "\nTask 9 conversion-quality check "
        "completed successfully."
    )

else:

    print(
        "No relevance regression detected : FAIL"
    )

    print(
        "Relevance regression requires investigation."
    )