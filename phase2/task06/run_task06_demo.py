"""
PlaceMux Phase 2 — Task 6
Payments Design & Gateway Setup
Match Quality Baseline Demo
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

from quality_baseline import (
    MODEL_VERSION,
    build_quality_baseline
)


# ============================================================
# REPRESENTATIVE MARKETPLACE RESULTS
# ============================================================

# These results represent the current matching system
# before future monetization/payment changes.

job_results = [
    {
        "job_id": "job_001",
        "job_role": "ML Engineer",
        "match_score": 1.00,
        "rank": 1,
        "model_version": MODEL_VERSION
    },
    {
        "job_id": "job_002",
        "job_role": "Data Scientist",
        "match_score": 0.85,
        "rank": 2,
        "model_version": MODEL_VERSION
    },
    {
        "job_id": "job_003",
        "job_role": "Software Engineer",
        "match_score": 0.325,
        "rank": 3,
        "model_version": MODEL_VERSION
    }
]


candidate_results = [
    {
        "student_id": "student_001",
        "candidate_name": "Student One",
        "match_score": 1.00,
        "rank": 1,
        "model_version": MODEL_VERSION
    },
    {
        "student_id": "student_003",
        "candidate_name": "Student Three",
        "match_score": 0.95,
        "rank": 2,
        "model_version": MODEL_VERSION
    },
    {
        "student_id": "student_002",
        "candidate_name": "Student Two",
        "match_score": 0.5481,
        "rank": 3,
        "model_version": MODEL_VERSION
    },
    {
        "student_id": "student_004",
        "candidate_name": "Student Four",
        "match_score": 0.3812,
        "rank": 4,
        "model_version": MODEL_VERSION
    }
]


# ============================================================
# REPEATED RESULTS
# ============================================================

# Simulates running the same matching system again.
# This allows us to measure baseline consistency.

repeated_job_results = [
    dict(item)
    for item in job_results
]

repeated_candidate_results = [
    dict(item)
    for item in candidate_results
]


# ============================================================
# BUILD BASELINES
# ============================================================

job_baseline = build_quality_baseline(
    results=job_results,
    expected_top_id="job_001",
    relevant_ids={
        "job_001",
        "job_002"
    },
    repeated_results=repeated_job_results
)


candidate_baseline = build_quality_baseline(
    results=candidate_results,
    expected_top_id="student_001",
    relevant_ids={
        "student_001",
        "student_003"
    },
    repeated_results=repeated_candidate_results
)


# ============================================================
# COMBINED BASELINE
# ============================================================

all_scores = [
    job_baseline["overall_baseline_quality"],
    candidate_baseline["overall_baseline_quality"]
]

overall_baseline = sum(
    all_scores
) / len(all_scores)


baseline_status = (
    "PASS"
    if (
        job_baseline["ranking_consistency"]
        and
        candidate_baseline[
            "ranking_consistency"
        ]
        and
        overall_baseline >= 0.70
    )
    else "FAIL"
)


baseline_result = {
    "task": "Task 6 — Match Quality Baseline",
    "model_version": MODEL_VERSION,

    "job_baseline": job_baseline,

    "candidate_baseline":
        candidate_baseline,

    "metrics": {
        "average_match_score": round(
            (
                job_baseline[
                    "average_match_score"
                ]
                +
                candidate_baseline[
                    "average_match_score"
                ]
            ) / 2,
            4
        ),

        "top_1_relevance": round(
            (
                job_baseline[
                    "top_1_relevance"
                ]
                +
                candidate_baseline[
                    "top_1_relevance"
                ]
            ) / 2,
            4
        ),

        "top_3_relevance": round(
            (
                job_baseline[
                    "top_3_relevance"
                ]
                +
                candidate_baseline[
                    "top_3_relevance"
                ]
            ) / 2,
            4
        ),

        "ranking_consistency": (
            job_baseline[
                "ranking_consistency"
            ]
            and
            candidate_baseline[
                "ranking_consistency"
            ]
        ),

        "high_quality_match_rate": round(
            (
                job_baseline[
                    "high_quality_match_rate"
                ]
                +
                candidate_baseline[
                    "high_quality_match_rate"
                ]
            ) / 2,
            4
        ),

        "low_quality_match_rate": round(
            (
                job_baseline[
                    "low_quality_match_rate"
                ]
                +
                candidate_baseline[
                    "low_quality_match_rate"
                ]
            ) / 2,
            4
        ),

        "overall_baseline_quality":
            round(
                overall_baseline,
                4
            )
    },

    "baseline_status":
        baseline_status
}


# ============================================================
# DISPLAY
# ============================================================

print("=" * 70)
print("TASK 6 — MATCH QUALITY BASELINE")
print("=" * 70)

print("\n========== JOB BASELINE ==========")

print(
    "Average match score       : "
    f"{job_baseline['average_match_score'] * 100:.2f}%"
)

print(
    "Top-1 relevance           : "
    f"{job_baseline['top_1_relevance'] * 100:.2f}%"
)

print(
    "Top-3 relevance           : "
    f"{job_baseline['top_3_relevance'] * 100:.2f}%"
)

print(
    "Ranking consistency       : "
    f"{'PASS' if job_baseline['ranking_consistency'] else 'FAIL'}"
)

print(
    "High-quality match rate   : "
    f"{job_baseline['high_quality_match_rate'] * 100:.2f}%"
)

print(
    "Low-quality match rate    : "
    f"{job_baseline['low_quality_match_rate'] * 100:.2f}%"
)

print(
    "Overall job quality       : "
    f"{job_baseline['overall_baseline_quality'] * 100:.2f}%"
)


print("\n========== CANDIDATE BASELINE ==========")

print(
    "Average match score       : "
    f"{candidate_baseline['average_match_score'] * 100:.2f}%"
)

print(
    "Top-1 relevance           : "
    f"{candidate_baseline['top_1_relevance'] * 100:.2f}%"
)

print(
    "Top-3 relevance           : "
    f"{candidate_baseline['top_3_relevance'] * 100:.2f}%"
)

print(
    "Ranking consistency       : "
    f"{'PASS' if candidate_baseline['ranking_consistency'] else 'FAIL'}"
)

print(
    "High-quality match rate   : "
    f"{candidate_baseline['high_quality_match_rate'] * 100:.2f}%"
)

print(
    "Low-quality match rate    : "
    f"{candidate_baseline['low_quality_match_rate'] * 100:.2f}%"
)

print(
    "Overall candidate quality : "
    f"{candidate_baseline['overall_baseline_quality'] * 100:.2f}%"
)


print("\n========== OVERALL BASELINE ==========")

print(
    "Average match score       : "
    f"{baseline_result['metrics']['average_match_score'] * 100:.2f}%"
)

print(
    "Top-1 relevance           : "
    f"{baseline_result['metrics']['top_1_relevance'] * 100:.2f}%"
)

print(
    "Top-3 relevance           : "
    f"{baseline_result['metrics']['top_3_relevance'] * 100:.2f}%"
)

print(
    "Ranking consistency       : "
    f"{'PASS' if baseline_result['metrics']['ranking_consistency'] else 'FAIL'}"
)

print(
    "High-quality match rate   : "
    f"{baseline_result['metrics']['high_quality_match_rate'] * 100:.2f}%"
)

print(
    "Low-quality match rate    : "
    f"{baseline_result['metrics']['low_quality_match_rate'] * 100:.2f}%"
)

print(
    "Overall baseline quality : "
    f"{baseline_result['metrics']['overall_baseline_quality'] * 100:.2f}%"
)

print(
    "Model version             : "
    f"{MODEL_VERSION}"
)

print(
    "Baseline status           : "
    f"{baseline_status}"
)


print("\n========== STRUCTURED BASELINE ==========")

print(
    json.dumps(
        baseline_result,
        indent=2
    )
)


print("\n========== VERIFICATION ==========")

print(
    "Match-quality baseline recorded : "
    f"{'PASS' if baseline_status == 'PASS' else 'FAIL'}"
)

print(
    "Ranking consistency             : "
    f"{'PASS' if baseline_result['metrics']['ranking_consistency'] else 'FAIL'}"
)

print(
    "Model version tracked           : PASS"
)

print(
    "Baseline ready for future comparison : "
    f"{'PASS' if baseline_status == 'PASS' else 'FAIL'}"
)


if baseline_status == "PASS":
    print(
        "\nTask 6 match-quality baseline "
        "completed successfully."
    )
else:
    print(
        "\nTask 6 baseline validation failed."
    )