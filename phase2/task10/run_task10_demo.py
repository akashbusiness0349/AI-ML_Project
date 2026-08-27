"""
PlaceMux Phase 2 — Task 10
Monetization Integration & Revenue Dashboard

Matching Quality Sign-off Demo
"""

import json
import sys
from pathlib import Path


# Allow importing from phase2/task10/src
CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from quality_signoff import evaluate_quality_signoff


# ============================================================
# TASK 6 — MATCH QUALITY BASELINE
# ============================================================

baseline_metrics = {
    "average_match_score": 0.725,
    "top_1_relevance": 1.0,
    "top_3_relevance": 0.6667,
    "ranking_consistency": True,
    "high_quality_match_rate": 0.6667,
    "low_quality_match_rate": 0.3333
}


# ============================================================
# POST-MONETIZATION QUALITY
# Based on the validated Task 9 post-paywall results
# ============================================================

post_monetization_metrics = {
    "average_match_score": 0.725,
    "top_1_relevance": 1.0,
    "top_3_relevance": 0.6667,
    "ranking_consistency": True,
    "high_quality_match_rate": 0.6667,
    "low_quality_match_rate": 0.3333
}


# ============================================================
# QUALITY SIGN-OFF
# ============================================================

result = evaluate_quality_signoff(
    baseline_metrics=baseline_metrics,
    post_monetization_metrics=post_monetization_metrics,
    allowed_relevance_drop=0.05
)


# ============================================================
# DISPLAY
# ============================================================

print("=" * 70)
print("TASK 10 — MONETIZATION INTEGRATION & QUALITY SIGN-OFF")
print("=" * 70)


print("\n========== BASELINE — TASK 6 ==========")

print(
    f"Average match score       : "
    f"{baseline_metrics['average_match_score'] * 100:.2f}%"
)

print(
    f"Top-1 relevance           : "
    f"{baseline_metrics['top_1_relevance'] * 100:.2f}%"
)

print(
    f"Top-3 relevance           : "
    f"{baseline_metrics['top_3_relevance'] * 100:.2f}%"
)

print(
    f"Ranking consistency       : "
    f"{'PASS' if baseline_metrics['ranking_consistency'] else 'FAIL'}"
)

print(
    f"High-quality match rate   : "
    f"{baseline_metrics['high_quality_match_rate'] * 100:.2f}%"
)

print(
    f"Low-quality match rate    : "
    f"{baseline_metrics['low_quality_match_rate'] * 100:.2f}%"
)


print("\n========== POST-MONETIZATION — TASK 9 ==========")

print(
    f"Average match score       : "
    f"{post_monetization_metrics['average_match_score'] * 100:.2f}%"
)

print(
    f"Top-1 relevance           : "
    f"{post_monetization_metrics['top_1_relevance'] * 100:.2f}%"
)

print(
    f"Top-3 relevance           : "
    f"{post_monetization_metrics['top_3_relevance'] * 100:.2f}%"
)

print(
    f"Ranking consistency       : "
    f"{'PASS' if post_monetization_metrics['ranking_consistency'] else 'FAIL'}"
)

print(
    f"High-quality match rate   : "
    f"{post_monetization_metrics['high_quality_match_rate'] * 100:.2f}%"
)

print(
    f"Low-quality match rate    : "
    f"{post_monetization_metrics['low_quality_match_rate'] * 100:.2f}%"
)


print("\n========== BASELINE VS POST-MONETIZATION ==========")

comparison = result["comparison"]

print(
    f"Average match score change       : "
    f"{comparison['average_match_score_change'] * 100:+.2f}%"
)

print(
    f"Top-1 relevance change           : "
    f"{comparison['top_1_relevance_change'] * 100:+.2f}%"
)

print(
    f"Top-3 relevance change           : "
    f"{comparison['top_3_relevance_change'] * 100:+.2f}%"
)

print(
    f"High-quality match rate change   : "
    f"{comparison['high_quality_match_rate_change'] * 100:+.2f}%"
)

print(
    f"Low-quality match rate change    : "
    f"{comparison['low_quality_match_rate_change'] * 100:+.2f}%"
)


print("\n========== QUALITY CHECKS ==========")

checks = result["quality_checks"]

print(
    f"Ranking consistency       : "
    f"{'PASS' if checks['ranking_consistency'] else 'FAIL'}"
)

print(
    f"Relevance protected       : "
    f"{'PASS' if checks['relevance_protected'] else 'FAIL'}"
)

print(
    f"No ranking bias          : "
    f"{'PASS' if checks['no_ranking_bias'] else 'FAIL'}"
)

print(
    f"No quality regression    : "
    f"{'PASS' if checks['no_quality_regression'] else 'FAIL'}"
)

print(
    f"Allowed relevance drop   : "
    f"{checks['allowed_relevance_drop'] * 100:.2f}%"
)

print(
    f"Overall quality check    : "
    f"{'PASS' if checks['overall_quality_check'] else 'FAIL'}"
)


print("\n========== FINAL QUALITY SIGN-OFF ==========")

sign_off = result["sign_off"]

print(
    f"Matching quality status : "
    f"{sign_off['matching_quality_status']}"
)

print(
    f"Monetization regression : "
    f"{'DETECTED' if sign_off['monetization_regression'] else 'NOT DETECTED'}"
)

print(
    f"Decision                : "
    f"{sign_off['decision']}"
)

print(
    f"Reason                  : "
    f"{sign_off['reason']}"
)


print("\n========== STRUCTURED SIGN-OFF RESULT ==========")

structured_result = {
    "task": "Task 10 — Monetization Integration & Revenue Dashboard",
    "model_version": "v1-quality-signoff",
    "baseline_metrics": baseline_metrics,
    "post_monetization_metrics": post_monetization_metrics,
    "comparison": result["comparison"],
    "quality_checks": result["quality_checks"],
    "sign_off": result["sign_off"],
    "final_status": result["final_status"]
}

print(
    json.dumps(
        structured_result,
        indent=2
    )
)


print("\n========== FINAL STATUS ==========")

print(
    "Matching quality signed off : "
    + ("PASS" if result["final_status"] == "PASS" else "FAIL")
)

print(
    "Monetization degradation    : "
    + (
        "NOT DETECTED"
        if not sign_off["monetization_regression"]
        else "DETECTED"
    )
)

print(
    "Quality regression check    : "
    + (
        "PASS"
        if checks["no_quality_regression"]
        else "FAIL"
    )
)

print(
    "Overall sign-off            : "
    + (
        "PASS"
        if checks["overall_quality_check"]
        else "FAIL"
    )
)

print("\nTask 10 matching quality sign-off completed successfully.")